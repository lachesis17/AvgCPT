import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import math
import scipy as sc
import sys
sys.stdout.reconfigure(encoding='utf-8')

class DesignProfile():
    def profile(param, depth, name):
        if param.empty or depth.empty:
            return
        if len(param) == 1:
            return
        
        param = np.array(param)
        depth = np.array(depth)

        inital_regression = sc.stats.linregress(depth,param)

        if math.isnan(inital_regression[0]):
            return

        std = np.array(param).std()

        print(f'''initial regression:
{inital_regression}''')

        r2 = inital_regression[2]**2
        r2_cor = (1-(1-r2)*(len(param)-1)/(len(param)-1-1))
        std_err_y_est = np.sqrt(1-r2_cor)*std
        slope = inital_regression[0]
        intrcpt = inital_regression[1]

        print(f'standard error y estimate: {std_err_y_est}')

        new_dep = []
        new_param = []
        for y in range(0,len(param)):
            if not (slope * depth[y] + intrcpt + std_err_y_est * 1.96) <= param[y] and not (slope * depth[y] + intrcpt + std_err_y_est * 1.96) <= param[y]:
                new_dep.append(depth[y])
                new_param.append(param[y])

        profile = sc.stats.linregress(new_dep,new_param)

        std_new = np.array(new_param).std()
        r2_new = profile[2]**2
        r2_cor_new = (1-(1-r2_new)*(len(new_param)-1)/(len(new_param)-2))
        std_err_y_est_new = np.sqrt(1-r2_cor_new)*std_new

        print(f'''new linear regression on new dataset without outliers:
{profile}''')

        bot_lb = profile[0] * depth[0] + profile[1] - std_err_y_est_new * 0.68
        bot_ub = profile[0] * depth[0] + profile[1] + std_err_y_est_new * 0.68
        bot_be = profile[0] * depth[0] + profile[1]

        top_lb = profile[0] * depth[-1] + profile[1] - std_err_y_est_new * 0.68
        top_ub = profile[0] * depth[-1] + profile[1] + std_err_y_est_new * 0.68
        top_be = profile[0] * depth[-1] + profile[1]

        print('------------------------------------------')
        print(f'BOT | Lower: {bot_lb}, Upper: {top_lb}')
        print(f'TOP | Lower: {bot_ub}, Upper: {top_ub}')
        print(f'BE | Lower: {bot_be}, Upper: {top_be}')
        print('------------------------------------------')
        lb = [bot_lb, top_lb]
        ub = [bot_ub, top_ub]
        be = [bot_be, top_be]

        #plotting
        plt.rcParams.update({'font.size': 8})
        fig, graph = plt.subplots(1, 1, figsize=(4.5,7.0))
        fig.canvas.manager.set_window_title('cpt profile')
        fig.tight_layout()

        plt.subplots_adjust(
        left  = 0.1,
        right = 0.925,
        bottom = 0.1,
        top = 0.9,
        wspace = 0.2,
        hspace = 0.2,
        )

        graph.plot(lb, [depth[0],depth[-1]],color = 'r',alpha = 0.5, label = 'lower bounds')
        graph.plot(ub, [depth[0],depth[-1]],color = 'g',alpha = 0.5, label = 'upper bounds')
        graph.plot(be, [depth[0],depth[-1]],color = 'black',alpha = 0.5, label = 'best estimate')
        graph.title.set_text(f'{name}')

        graph.scatter(param, depth, s=12, color = 'b', label = 'qc')
        graph.invert_yaxis()
        graph.legend()
        graph.set_ylabel('depth (m)')
        graph.set_xlabel(f'{str(name).split("-")[0]}', loc='left')
        plt.show()

        return [be, lb, ub]