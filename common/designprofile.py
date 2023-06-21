import numpy as np
from matplotlib import pyplot as plt
import math
import scipy as sc
import sys
sys.stdout.reconfigure(encoding='utf-8')

class DesignProfile():    
    def profile(param:list, depth:list, name:str, model:str, zvalue:int, plot:bool) -> list:
        """
        Perform statistical analysis on two lists (x,y) for linear regression (scipy) to determine best estimate, lower and upper bounds of (x) data.
        Removes outliers with independant or dependant models and returns list of lists with top/bot bot values of best estimate, lower bounds, upper bounds as: [[be_top,be_bot][lb_top,lb_bot][ub_top,ub_bot]]

        Parameters
        ----------
        param : (x) list or column from pandas dataframe - converted to numpy array 

        depth: (y) list or column from pandas dataframe - converted to numpy array 

        name : str for description of param, used to pass units for plotting if used, or to preserve desired data (e.g. borehole, layer)

        model : str = "DEP", "IND", "AUTO"

            "DEP" : for Dependant model, removes outliers of (x) data with linear regression and depth (y) with:
            slope * depth + intercept + standard error of y estimate * 1.96

            "IND" : for Independant model, removes outliers of (x) data with mean and standard deviation with:
            mean -/+ standard deviation * 1.96

            "AUTO" : selects model based on the lesser standard deviation of both models

        zvalue : int = 70, 75, 90, 95

            pass an int to select "confidence level" of lower/upper bounds based on table of normal distribtion with:

            70 = 70% & 30% confidence

            75 = 75% & 25% confidence

            90 = 90% & 10% confidence

            95 = 95% & 5% confidence

        plot : bool = True for plotting (x,y) with matplotlib for QA of model type or upper/lower bounds and best estimate
            """

        if param.empty or depth.empty:
            return
        if len(param) == 1:
            return
        
        if zvalue == 70:
            z_val = 0.53
        if zvalue == 75:
            z_val = 0.68
        if zvalue == 90:
            z_val = 1.29
        if zvalue == 95:
            z_val = 1.65
        
        param = np.array(param)
        depth = np.array(depth)

        inital_regression = sc.stats.linregress(depth,param)

        if math.isnan(inital_regression[0]):
            return

        mean = np.array(param).mean()
        std = np.array(param).std()

        print(f'''initial regression:
{inital_regression}''')

        n = len(param) # number of observations
        r2 = inital_regression[2]**2 # R squared
        r2_cor = (1-(1-r2)*(n-1)/(n-1-1)) # R squared corrected
        std_err_y_est = np.sqrt(1-r2_cor)*std # standard error y estimate from R squared corrected
        slope = inital_regression[0] # slope from linear regressions
        intrcpt = inital_regression[1] # intercept from linear regression

        print(f'standard error y estimate: {std_err_y_est}')


        '''dependent model'''

        depth_DEP = []
        param_DEP = []
        for y in range(0,len(param)):
            if not (slope * depth[y] + intrcpt + std_err_y_est * 1.96) <= param[y] and not (slope * depth[y] + intrcpt + std_err_y_est * 1.96) <= param[y]:
                depth_DEP.append(depth[y])
                param_DEP.append(param[y])

        profile_DEP = sc.stats.linregress(depth_DEP,param_DEP) # new dataset with outliers removed

        n_DEP = len(param_DEP)
        mean_new_DEP = np.array(param_DEP).mean()
        std_new_DEP = np.array(param_DEP).std()
        r2_new_DEP = profile_DEP[2]**2
        r2_cor_new_DEP = (1-(1-r2_new_DEP)*(n_DEP-1)/(n_DEP-2))
        std_err_y_est_new_DEP = np.sqrt(1-r2_cor_new_DEP)*std_new_DEP


        '''independent model'''

        depth_IND = []
        param_IND = []
        for y in range(0,len(param)):
            if (mean - std * 1.96) <= param[y] and param[y] <= (mean + std * 1.96):
                depth_IND.append(depth[y])
                param_IND.append(param[y])

        mean_new_IND = np.array(param_IND).mean() # new mean on dataset with outliers removed
        std_new_IND = np.array(param_IND).std() # new standard deviations on dataset with outliers removed

        profile_IND = [mean_new_IND, std_new_IND]

        if model == "DEP":
            mode = "DEPENDANT"
            print(f'''~DEPENDANT~
new linear regression on new dataset without outliers:
{profile_DEP}''')

            bot_lb = profile_DEP[0] * depth[0] + profile_DEP[1] - std_err_y_est_new_DEP * z_val
            bot_ub = profile_DEP[0] * depth[0] + profile_DEP[1] + std_err_y_est_new_DEP * z_val
            bot_be = profile_DEP[0] * depth[0] + profile_DEP[1]

            top_lb = profile_DEP[0] * depth[-1] + profile_DEP[1] - std_err_y_est_new_DEP * z_val
            top_ub = profile_DEP[0] * depth[-1] + profile_DEP[1] + std_err_y_est_new_DEP * z_val
            top_be = profile_DEP[0] * depth[-1] + profile_DEP[1]

            print('------------------------------------------')
            print(name,mode)
            print(f'BOT | Lower: {bot_lb}, Upper: {top_lb}')
            print(f'TOP | Lower: {bot_ub}, Upper: {top_ub}')
            print(f'BE | Lower: {bot_be}, Upper: {top_be}')
            print('------------------------------------------')
            lb = [bot_lb, top_lb]
            ub = [bot_ub, top_ub]
            be = [bot_be, top_be]

        if model == "IND":
            mode = "INDEPENDANT"
            print(f'''~INDEPENDANT~
independant mean and standard deviation:
{profile_IND}''')
            
            bot_lb = profile_IND[0] - profile_IND[1] * z_val
            bot_ub = profile_IND[0] + profile_IND[1] * z_val
            bot_be = profile_IND[0] 

            top_lb = profile_IND[0] - profile_IND[1] * z_val
            top_ub = profile_IND[0] + profile_IND[1] * z_val
            top_be = profile_IND[0] 

            print('------------------------------------------')
            print(name,mode)
            print(f'BOT | Lower: {bot_lb}, Upper: {top_lb}')
            print(f'TOP | Lower: {bot_ub}, Upper: {top_ub}')
            print(f'BE | Lower: {bot_be}, Upper: {top_be}')
            print('------------------------------------------')
            lb = [bot_lb, top_lb]
            ub = [bot_ub, top_ub]
            be = [bot_be, top_be]

        '''auto model''' # determines best model to use based on lesser value of standard deviation of new dataset of each model 

        if model == "AUTO":
            if std_new_IND < std_new_DEP:
                mode = "INDEPENDANT"
                print(f'''~INDEPENDANT~
independant mean and standard deviation:
{profile_IND}''')
                
                bot_lb = profile_IND[0] - profile_IND[1] * z_val
                bot_ub = profile_IND[0] + profile_IND[1] * z_val
                bot_be = profile_IND[0] 

                top_lb = profile_IND[0] - profile_IND[1] * z_val
                top_ub = profile_IND[0] + profile_IND[1] * z_val
                top_be = profile_IND[0] 

                print('------------------------------------------')
                print(name,mode)
                print(f'BOT | Lower: {bot_lb}, Upper: {top_lb}')
                print(f'TOP | Lower: {bot_ub}, Upper: {top_ub}')
                print(f'BE | Lower: {bot_be}, Upper: {top_be}')
                print('------------------------------------------')
                lb = [bot_lb, top_lb]
                ub = [bot_ub, top_ub]
                be = [bot_be, top_be]
            else:
                mode = "DEPENDANT"
                print(f'''~DEPENDANT~
new linear regression on new dataset without outliers:
{profile_DEP}''')

                bot_lb = profile_DEP[0] * depth[0] + profile_DEP[1] - std_err_y_est_new_DEP * z_val
                bot_ub = profile_DEP[0] * depth[0] + profile_DEP[1] + std_err_y_est_new_DEP * z_val
                bot_be = profile_DEP[0] * depth[0] + profile_DEP[1]

                top_lb = profile_DEP[0] * depth[-1] + profile_DEP[1] - std_err_y_est_new_DEP * z_val
                top_ub = profile_DEP[0] * depth[-1] + profile_DEP[1] + std_err_y_est_new_DEP * z_val
                top_be = profile_DEP[0] * depth[-1] + profile_DEP[1]

                print('------------------------------------------')
                print(name,mode)
                print(f'BOT | Lower: {bot_lb}, Upper: {top_lb}')
                print(f'TOP | Lower: {bot_ub}, Upper: {top_ub}')
                print(f'BE | Lower: {bot_be}, Upper: {top_be}')
                print('------------------------------------------')
                lb = [bot_lb, top_lb]
                ub = [bot_ub, top_ub]
                be = [bot_be, top_be]
        
        if plot == True:
            DesignProfile.plotting(depth,param,lb,ub,be,name,mode)

        return [be, lb, ub]
    
    
    def plotting(depth, param, lb, ub, be, name, mode):
        plt.rcParams.update({'font.size': 8})
        fig, graph = plt.subplots(1, 1, figsize=(5,7.0))
        fig.canvas.manager.set_window_title('cpt profile')
        fig.tight_layout()

        plt.subplots_adjust(left  = 0.1, right = 0.925, bottom = 0.1, top = 0.9, wspace = 0.2, hspace = 0.2)

        graph.plot(lb, [depth[0],depth[-1]],color = 'r',alpha = 0.5, label = 'lower bounds')
        graph.plot(ub, [depth[0],depth[-1]],color = 'g',alpha = 0.5, label = 'upper bounds')
        graph.plot(be, [depth[0],depth[-1]],color = 'black',alpha = 0.5, label = 'best estimate')
        graph.title.set_text(f'{name} - {mode}')

        graph.scatter(param, depth, s=12, color = 'b', label = 'qc')
        graph.invert_yaxis()
        graph.legend()
        graph.set_ylabel('depth (m)')
        graph.set_xlabel(f'{str(name).split("-")[0]}', loc='left')
        plt.show()
