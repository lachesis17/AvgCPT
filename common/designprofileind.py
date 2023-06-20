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

        mean = np.array(param).mean()
        std = np.array(param).std()

        print(f'''initial regression:
{inital_regression}''')

        r2 = inital_regression[2]**2
        r2_cor = (1-(1-r2)*(len(param)-1)/(len(param)-1-1))
        std_err_y_est = np.sqrt(1-r2_cor)*std
        slope = inital_regression[0]
        intrcpt = inital_regression[1]

        print(f'standard error y estimate: {std_err_y_est}')


#Setting up the z value for Lower Bound and Upper Bound, for any given quantile / percentile (Table of the normal distribution)
# (30%,70% OR 25%,75% OR 10%,90% OR 5%,95%)

        z_value_70 = 0.53
        z_value_75 = 0.68
        z_value_90 = 1.29
        z_value_95 = 1.65

        '''dependent model'''

        depth_DEP = []
        param_DEP = []
        for y in range(0,len(param)):
            if not (slope * depth[y] + intrcpt + std_err_y_est * 1.96) <= param[y] and not (slope * depth[y] + intrcpt + std_err_y_est * 1.96) <= param[y]:
                depth_DEP.append(depth[y])
                param_DEP.append(param[y])

        profile_DEP = sc.stats.linregress(depth_DEP,param_DEP)

        mean_new_DEP = np.array(param_DEP).mean()
        std_new_DEP = np.array(param_DEP).std()
        r2_new_DEP = profile_DEP[2]**2
        r2_cor_new_DEP = (1-(1-r2_new_DEP)*(len(param_DEP)-1)/(len(param_DEP)-2))
        std_err_y_est_new_DEP = np.sqrt(1-r2_cor_new_DEP)*std_new_DEP


        print(f"mean - std: {mean - std * 1.96}")
        print(f"mean + std: {mean + std * 1.96}")

        '''independent model'''

        depth_IND = []
        param_IND = []
        for y in range(0,len(param)):
            if (mean - std * 1.96) <= param[y] and param[y] <= (mean + std * 1.96):
                depth_IND.append(depth[y])
                param_IND.append(param[y])

        if not param_IND == [] and not len(param_IND) <= 2:
            mean_new_IND = np.array(param_IND).mean()
            std_new_IND = np.array(param_IND).std()

            profile_IND = [mean_new_IND, std_new_IND]

            '''determine best model'''
            if std_new_IND < std_new_DEP:
                model = "INDEPENDANT"
                print(f'''~INDEPENDANT~
independant mean and standard deviation:
{profile_IND}''')
                
                bot_lb = profile_IND[0] - profile_IND[1] * z_value_70
                bot_ub = profile_IND[0] + profile_IND[1] * z_value_70
                bot_be = profile_IND[0] 

                top_lb = profile_IND[0] - profile_IND[1] * z_value_70
                top_ub = profile_IND[0] + profile_IND[1] * z_value_70
                top_be = profile_IND[0] 

                print('------------------------------------------')
                print(f'BOT | Lower: {bot_lb}, Upper: {top_lb}')
                print(f'TOP | Lower: {bot_ub}, Upper: {top_ub}')
                print(f'BE | Lower: {bot_be}, Upper: {top_be}')
                print('------------------------------------------')
                lb = [bot_lb, top_lb]
                ub = [bot_ub, top_ub]
                be = [bot_be, top_be]

            else:
                model = "DEPENDANT"
                print(f'''~DEPENDANT~
new linear regression on new dataset without outliers:
{profile_DEP}''')

                bot_lb = profile_DEP[0] * depth[0] + profile_DEP[1] - std_err_y_est_new_DEP * z_value_70
                bot_ub = profile_DEP[0] * depth[0] + profile_DEP[1] + std_err_y_est_new_DEP * z_value_70
                bot_be = profile_DEP[0] * depth[0] + profile_DEP[1]

                top_lb = profile_DEP[0] * depth[-1] + profile_DEP[1] - std_err_y_est_new_DEP * z_value_70
                top_ub = profile_DEP[0] * depth[-1] + profile_DEP[1] + std_err_y_est_new_DEP * z_value_70
                top_be = profile_DEP[0] * depth[-1] + profile_DEP[1]

                print('------------------------------------------')
                print(f'BOT | Lower: {bot_lb}, Upper: {top_lb}')
                print(f'TOP | Lower: {bot_ub}, Upper: {top_ub}')
                print(f'BE | Lower: {bot_be}, Upper: {top_be}')
                print('------------------------------------------')
                lb = [bot_lb, top_lb]
                ub = [bot_ub, top_ub]
                be = [bot_be, top_be]

        else:
                model = "DEPENDANT"
                print(f'''~DEPENDANT~
new linear regression on new dataset without outliers:
{profile_DEP}''')

                bot_lb = profile_DEP[0] * depth[0] + profile_DEP[1] - std_err_y_est_new_DEP * z_value_70
                bot_ub = profile_DEP[0] * depth[0] + profile_DEP[1] + std_err_y_est_new_DEP * z_value_70
                bot_be = profile_DEP[0] * depth[0] + profile_DEP[1]

                top_lb = profile_DEP[0] * depth[-1] + profile_DEP[1] - std_err_y_est_new_DEP * z_value_70
                top_ub = profile_DEP[0] * depth[-1] + profile_DEP[1] + std_err_y_est_new_DEP * z_value_70
                top_be = profile_DEP[0] * depth[-1] + profile_DEP[1]

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

        print(name,model)

        graph.plot(lb, [depth[0],depth[-1]],color = 'r',alpha = 0.5, label = 'lower bounds')
        graph.plot(ub, [depth[0],depth[-1]],color = 'g',alpha = 0.5, label = 'upper bounds')
        graph.plot(be, [depth[0],depth[-1]],color = 'black',alpha = 0.5, label = 'best estimate')
        graph.title.set_text(f'{name} - {model}')

        graph.scatter(param, depth, s=12, color = 'b', label = 'qc')
        graph.invert_yaxis()
        graph.legend()
        graph.set_ylabel('depth (m)')
        graph.set_xlabel(f'{str(name).split("-")[0]}', loc='left')
        plt.show()

        return [be, lb, ub]