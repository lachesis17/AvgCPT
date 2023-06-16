import numpy as np
import pandas as pd
import math
import scipy as sc
import sys
sys.stdout.reconfigure(encoding='utf-8')

class DesignProfile():
    def profile(param, depth, name):
        if param.empty or depth.empty or len(param) <= 2:
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

        return [be, lb, ub]
