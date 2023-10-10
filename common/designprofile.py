import numpy as np
from matplotlib import pyplot as plt
import math
import scipy as sc
import sys
import pandas as pd
sys.stdout.reconfigure(encoding='utf-8')

class DesignProfile:    
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
        slope * depth + intercept -/+ standard error of y estimate * 1.96

        "IND" : for Independant model, removes outliers of (x) data with mean and standard deviation with:
        mean -/+ standard deviation * 1.96

        "AUTO" : selects model based on the lesser standard deviation of both models

        -/+ used to determine lower/upper bounds

    zvalue : int = 60, 65, 70, 75, 80, 85, 90, 95

        pass an int to select quantile of lower/upper bounds based on table of normal distribtion with examples:

        70 = 70% & 30% quantile

        75 = 75% & 25% quantile

        90 = 90% & 10% quantile

        95 = 95% & 5% quantile

    plot : bool = True for plotting (x,y) with matplotlib for QA of model type or upper/lower bounds and best estimate

    save : str = directory to save export of plots
    """
    
    def __init__(self, param, depth, name, model, zvalue, plot, save):
        self.param: list = param
        self.depth: list = depth
        self.name: str = name
        self.model: str = model
        self.zvalue: int = zvalue
        self.plot: bool = plot
        self.save: str = save
        self.depth_range: list = None
        self.mode: str = None
        self.quant_upp: str = None
        self.quant_low: str = None

    def profile(self) -> list:
        NoneType= type(None)

        if len(self.param) <= 4 or all(isinstance(x, NoneType) for x in self.param):
            return

        if any(isinstance(x, str) for x in self.param):
            param = [float(param) for iter,(param,depth) in enumerate(zip(self.param,self.depth)) if not param == ""]
            depth = [float(depth) for iter,(param,depth) in enumerate(zip(self.param,self.depth)) if not param == ""]
        param = [param for iter,(param,depth) in enumerate(zip(self.param,self.depth)) if not np.isnan(param)]
        depth = [depth for iter,(param,depth) in enumerate(zip(self.param,self.depth)) if not np.isnan(param)]

        if self.zvalue == 60:
            z_val = 0.26
            self.quant_upp = "60%"
            self.quant_low = "40%"
        if self.zvalue == 65:
            z_val = 0.39
            self.quant_upp = "65%"
            self.quant_low = "35%"
        if self.zvalue == 70:
            z_val = 0.53
            self.quant_upp = "70%"
            self.quant_low = "30%"
        if self.zvalue == 75:
            z_val = 0.68
            self.quant_upp = "75%"
            self.quant_low = "25%"
        if self.zvalue == 80:
            z_val = 0.85
            self.quant_upp = "80%"
            self.quant_low = "20%"
        if self.zvalue == 85:
            z_val = 1.04
            self.quant_upp = "85%"
            self.quant_low = "15%"
        if self.zvalue == 90:
            z_val = 1.29
            self.quant_upp = "90%"
            self.quant_low = "10%"
        if self.zvalue == 95:
            z_val = 1.65
            self.quant_upp = "95%"
            self.quant_low = "5%"
        
        param = np.array(param)
        depth = np.array(depth)
    
        if len(param) <= 4:
            return

        n = len(param) # number of observations

        # select tvalue for 95% confidence based on the number of observations (sample size)
            
        if n <= 5:
            tvalue = 2.015
        if n == 6:
            tvalue = 1.943
        if n == 7:
            tvalue = 1.895
        if n == 8:
            tvalue = 1.86
        if n == 9:
            tvalue = 1.833
        if n == 10:
            tvalue = 1.812
        if n == 11:
            tvalue = 1.796
        if n == 12:
            tvalue = 1.782
        if n == 13:
            tvalue = 1.771
        if n == 14:
            tvalue = 1.761
        if n == 15:
            tvalue = 1.753
        if n == 16:
            tvalue = 1.746
        if n == 17:
            tvalue = 1.74
        if n == 18:
            tvalue = 1.734
        if n == 19:
            tvalue = 1.729
        if n == 20:
            tvalue = 1.725
        if n == 21:
            tvalue = 1.721
        if n == 22:
            tvalue = 1.717
        if n == 23:
            tvalue = 1.714
        if n == 24:
            tvalue = 1.711
        if n == 25:
            tvalue = 1.708
        if n == 26:
            tvalue = 1.706
        if n == 27:
            tvalue = 1.703
        if n == 28:
            tvalue = 1.701
        if n == 29:
            tvalue = 1.699
        if n == 30:
            tvalue = 1.697
        if n > 30 and n <= 35:
            tvalue = 1.69
        if n > 35 and n <= 40:
            tvalue = 1.684
        if n > 40 and n <= 45:
            tvalue = 1.679
        if n > 45 and n <= 50:
            tvalue = 1.676
        if n > 50 and n <= 60:
            tvalue = 1.671
        if n > 60 and n <= 70:
            tvalue = 1.667
        if n > 70 and n <= 80:
            tvalue = 1.664
        if n > 80 and n <= 100:
            tvalue = 1.66
        if n > 100:
            tvalue = 1.645

        inital_regression = sc.stats.linregress(depth,param)

        if math.isnan(inital_regression[0]) or inital_regression[2] == 0.0:
            print('help')
            return

        mean = np.array(param).mean()
        std = np.array(param).std()

        #print(f'''initial regression:
#{inital_regression}''')

        r2 = inital_regression[2]**2 # R squared
        r2_cor = (1-(1-r2)*(n-1)/(n-1-1)) # R squared corrected
        std_err_y_est = np.sqrt(1-r2_cor)*std # standard error y estimate from R squared corrected
        slope = inital_regression[0] # slope from linear regressions
        intrcpt = inital_regression[1] # intercept from linear regression

        #print(f'standard error y estimate: {std_err_y_est}')


        '''dependent model'''

        param_DEP = [param for iter,(param,depth) in enumerate(zip(param,depth)) if param >= (slope * depth + intrcpt - std_err_y_est * 1.96) and param <= (slope * depth + intrcpt + std_err_y_est * 1.96)]
        depth_DEP = [depth for iter,(param,depth) in enumerate(zip(param,depth)) if param >= (slope * depth + intrcpt - std_err_y_est * 1.96) and param <= (slope * depth + intrcpt + std_err_y_est * 1.96)]

        profile_DEP = sc.stats.linregress(depth_DEP,param_DEP) # new dataset with outliers removed

        n_DEP = len(param_DEP)
        mean_new_DEP = np.array(param_DEP).mean()
        std_new_DEP = np.array(param_DEP).std()
        r2_new_DEP = profile_DEP[2]**2
        r2_cor_new_DEP = (1-(1-r2_new_DEP)*(n_DEP-1)/(n_DEP-2))
        std_err_y_est_new_DEP = np.sqrt(1-r2_cor_new_DEP)*std_new_DEP


        '''independent model'''

        param_IND = [param for iter,(param,depth) in enumerate(zip(param,depth)) if param >= (mean - std * 1.96) and param <= (mean + std * 1.96)]

        mean_new_IND = np.array(param_IND).mean() # new mean on dataset with outliers removed
        std_new_IND = np.array(param_IND).std() # new standard deviations on dataset with outliers removed

        profile_IND = [mean_new_IND, std_new_IND]

        if self.model == "DEP":
            self.mode = "Depth Dependent"
            #print(f'''~DEPENDENT~
#new linear regression on new dataset without outliers
#{profile_DEP}''')

            top_lb = profile_DEP[0] * depth[0] + profile_DEP[1] - std_err_y_est_new_DEP * z_val
            top_ub = profile_DEP[0] * depth[0] + profile_DEP[1] + std_err_y_est_new_DEP * z_val
            top_be = profile_DEP[0] * depth[0] + profile_DEP[1]

            bot_lb = profile_DEP[0] * depth[-1] + profile_DEP[1] - std_err_y_est_new_DEP * z_val
            bot_ub = profile_DEP[0] * depth[-1] + profile_DEP[1] + std_err_y_est_new_DEP * z_val
            bot_be = profile_DEP[0] * depth[-1] + profile_DEP[1]

            low_mean_95_top = profile_DEP[0] * depth[0] + profile_DEP[1] - tvalue * std * (np.sqrt((1 / n) + (3 * n / (n * n - 1))))
            low_mean_95_bot = profile_DEP[0] * depth[-1] + profile_DEP[1] - tvalue * std * (np.sqrt((1 / n) + (3 * n / (n * n - 1))))

            upp_mean_95_top = profile_DEP[0] * depth[0] + profile_DEP[1] + tvalue * std * (np.sqrt((1 / n) + (3 * n / (n * n - 1))))
            upp_mean_95_bot = profile_DEP[0] * depth[-1] + profile_DEP[1] + tvalue * std * (np.sqrt((1 / n) + (3 * n / (n * n - 1))))

            std2 = std_new_DEP
            mean2 = mean_new_DEP

            print('------------------------------------------')
            print(self.name,self.mode)
            print(f'Best Estimate | TOP: {top_be}, BOT: {bot_be}')
            print(f'Lower Bounds | TOP: {top_lb}, BOT: {bot_lb}')
            print(f'Upper Bounds | TOP: {top_ub}, BOT: {bot_ub}')
            print(f'Upper Mean 95% | TOP: {upp_mean_95_top}, BOT: {upp_mean_95_bot}')
            print(f'Lower Mean 95% | TOP: {low_mean_95_top}, BOT: {low_mean_95_bot}')
            print(f'Standard deviation (Before): {std}, (After): {std2}')
            print(f'Mean (Before): {mean}, (After): {mean2}')
            print('------------------------------------------')
            lb = [top_lb, bot_lb]
            ub = [top_ub, bot_ub]
            be = [top_be, bot_be]
            upp_mean_95 = [upp_mean_95_top, upp_mean_95_bot]
            low_mean_95 = [low_mean_95_top, low_mean_95_bot]
            std_arr = [std, std2]
            mean_arr = [mean, mean2]

        if self.model == "IND":
            self.mode = "Independent of Depth"
            #print(f'''~INDEPENDENT~
#independent mean and standard deviation:
#{profile_IND}''')
            
            top_lb = profile_IND[0] - profile_IND[1] * z_val
            top_ub = profile_IND[0] + profile_IND[1] * z_val
            top_be = profile_IND[0] 

            bot_lb = profile_IND[0] - profile_IND[1] * z_val
            bot_ub = profile_IND[0] + profile_IND[1] * z_val
            bot_be = profile_IND[0] 

            low_mean_95_top_bot = mean_new_IND - tvalue * (std / np.sqrt(n))
            upp_mean_95_top_bot = mean_new_IND + tvalue * (std / np.sqrt(n))

            std2 = std_new_IND
            mean2 = mean_new_IND

            print('------------------------------------------')
            print(self.name,self.mode)
            print(f'Best Estimate | TOP: {top_be}, BOT: {bot_be}')
            print(f'Lower Bounds | TOP: {top_lb}, BOT: {bot_lb}')
            print(f'Upper Bounds | TOP: {top_ub}, BOT: {bot_ub}')
            print(f'Upper Mean 95% | TOP: {upp_mean_95_top_bot}, BOT: {upp_mean_95_top_bot}')
            print(f'Lower Mean 95% | TOP: {low_mean_95_top_bot}, BOT: {low_mean_95_top_bot}')
            print(f'Standard deviation (Before): {std}, (After): {std2}')
            print(f'Mean (Before): {mean}, (After): {mean2}')
            print('------------------------------------------')
            lb = [top_lb, bot_lb]
            ub = [top_ub, bot_ub]
            be = [top_be, bot_be]
            upp_mean_95 = [upp_mean_95_top_bot, upp_mean_95_top_bot]
            low_mean_95 = [low_mean_95_top_bot, low_mean_95_top_bot]
            std_arr = [std, std2]
            mean_arr = [mean, mean2]

        '''auto model''' # determines best model to use based on lesser value of standard deviation of new dataset of each model 

        if self.model == "AUTO":
            if std_new_IND < std_new_DEP:
                self.mode = "Independent of Depth"
                #print(f'''~INDEPENDENT~
#independant mean and standard deviation:
#{profile_IND}''')
                
                top_lb = profile_IND[0] - profile_IND[1] * z_val
                top_ub = profile_IND[0] + profile_IND[1] * z_val
                top_be = profile_IND[0] 

                bot_lb = profile_IND[0] - profile_IND[1] * z_val
                bot_ub = profile_IND[0] + profile_IND[1] * z_val
                bot_be = profile_IND[0] 

                low_mean_95_top_bot = mean_new_IND - tvalue * (std / np.sqrt(n))
                upp_mean_95_top_bot = mean_new_IND + tvalue * (std / np.sqrt(n))

                std2 = std_new_IND
                mean2 = mean_new_IND

                print('------------------------------------------')
                print(self.name,self.mode)
                print(f'Best Estimate | TOP: {top_be}, BOT: {bot_be}')
                print(f'Lower Bounds | TOP: {top_lb}, BOT: {bot_lb}')
                print(f'Upper Bounds | TOP: {top_ub}, BOT: {bot_ub}')
                print(f'Upper Mean 95% | TOP: {upp_mean_95_top_bot}, BOT: {upp_mean_95_top_bot}')
                print(f'Lower Mean 95% | TOP: {low_mean_95_top_bot}, BOT: {low_mean_95_top_bot}')
                print(f'Standard deviation (Before): {std}, (After): {std2}')
                print(f'Mean (Before): {mean}, (After): {mean2}')
                print('------------------------------------------')
                lb = [top_lb, bot_lb]
                ub = [top_ub, bot_ub]
                be = [top_be, bot_be]
                upp_mean_95 = [upp_mean_95_top_bot, upp_mean_95_top_bot]
                low_mean_95 = [low_mean_95_top_bot, low_mean_95_top_bot]
                std_arr = [std, std2]
                mean_arr = [mean, mean2]

            else:
                self.mode = "Depth Dependent"
                #print(f'''~DEPENDENT~
#new linear regression on new dataset without outliers:
#{profile_DEP}''')

                top_lb = profile_DEP[0] * depth[0] + profile_DEP[1] - std_err_y_est_new_DEP * z_val
                top_ub = profile_DEP[0] * depth[0] + profile_DEP[1] + std_err_y_est_new_DEP * z_val
                top_be = profile_DEP[0] * depth[0] + profile_DEP[1]

                bot_lb = profile_DEP[0] * depth[-1] + profile_DEP[1] - std_err_y_est_new_DEP * z_val
                bot_ub = profile_DEP[0] * depth[-1] + profile_DEP[1] + std_err_y_est_new_DEP * z_val
                bot_be = profile_DEP[0] * depth[-1] + profile_DEP[1]

                low_mean_95_top = profile_DEP[0] * depth[0] + profile_DEP[1] - tvalue * std * (np.sqrt((1 / n) + (3 * n / (n * n - 1))))
                low_mean_95_bot = profile_DEP[0] * depth[-1] + profile_DEP[1] - tvalue * std * (np.sqrt((1 / n) + (3 * n / (n * n - 1))))

                upp_mean_95_top = profile_DEP[0] * depth[0] + profile_DEP[1] + tvalue * std * (np.sqrt((1 / n) + (3 * n / (n * n - 1))))
                upp_mean_95_bot = profile_DEP[0] * depth[-1] + profile_DEP[1] + tvalue * std * (np.sqrt((1 / n) + (3 * n / (n * n - 1))))

                std2 = std_new_DEP
                mean2 = mean_new_DEP

                print('------------------------------------------')
                print(self.name,self.mode)
                print(f'Best Estimate | TOP: {top_be}, BOT: {bot_be}')
                print(f'Lower Bounds | TOP: {top_lb}, BOT: {bot_lb}')
                print(f'Upper Bounds | TOP: {top_ub}, BOT: {bot_ub}')
                print(f'Upper Mean 95% | TOP: {upp_mean_95_top}, BOT: {upp_mean_95_bot}')
                print(f'Lower Mean 95% | TOP: {low_mean_95_top}, BOT: {low_mean_95_bot}')
                print(f'Standard deviation (Before): {std}, (After): {std2}')
                print(f'Mean (Before): {mean}, (After): {mean2}')
                print('------------------------------------------')
                lb = [top_lb, bot_lb]
                ub = [top_ub, bot_ub]
                be = [top_be, bot_be]
                upp_mean_95 = [upp_mean_95_top, upp_mean_95_bot]
                low_mean_95 = [low_mean_95_top, low_mean_95_bot]
                std_arr = [std, std2]
                mean_arr = [mean, mean2]

        if self.plot == True:
            self.plotting(depth, param, lb, ub, be, upp_mean_95, low_mean_95, self.quant_low, self.quant_upp, self.name, self.mode, self.save)

        return [be, lb, ub, upp_mean_95, low_mean_95, std_arr, mean_arr]
    
    
    def plotting(self, depth, param, lb, ub, be, upp_mean_95, low_mean_95, quant_low, quant_upp, name, mode, save):

        plt.rcParams.update({'font.size': 8})
        fig, graph = plt.subplots(1, 1, figsize=(7.0,12.5))
        fig.canvas.manager.set_window_title('Profile Lines')
        fig.tight_layout()

        plt.subplots_adjust(left  = 0.1, right = 0.925, bottom = 0.095, top = 0.89, wspace = 0.2, hspace = 0.2)

        graph.plot(lb, [depth[0],depth[-1]],color = 'r',alpha = 0.5, label = f'lower bounds {quant_low} quantile')
        graph.plot(ub, [depth[0],depth[-1]],color = 'g',alpha = 0.5, label = f'upper bounds {quant_upp} quantile')
        graph.plot(be, [depth[0],depth[-1]],color = 'black',alpha = 0.5, label = 'best estimate')
        graph.plot(upp_mean_95, [depth[0],depth[-1]],color = 'purple',alpha = 0.5, label = f'mean at 95% confidence', linestyle='dashed')
        graph.plot(low_mean_95, [depth[0],depth[-1]],color = 'purple',alpha = 0.5, linestyle='dashed')
        graph.set_title(f'{name} - {mode}', y=1.0, pad=35)
        unit = str(name).split("-")[0].split("(")[0]
        graph.scatter(param, depth, s=12, color = 'b', label = f'{unit}')
        graph.invert_yaxis()
        graph.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),ncol=3, fancybox=True, shadow=True)
        graph.set_ylabel('Depth (m)')
        graph.set_xlabel(f'{str(name).split("—")[0]}', loc='center')
        plt.savefig(f'{save}\{name} {mode}.pdf', dpi=200.0)
        #plt.show()

#TESTING
# df = pd.read_excel("50.xlsx", sheet_name="MC")
# df = df.sort_values(by=['depth'])
# df.reset_index(inplace=True)

# profile = DesignProfile()
# profile.model = "DEP"
# profile.zvalue = 75
# profile.plot = True
# profile.save = "C:/Users/Public/Documents"
# profile.param = df['mc']
# profile.depth = df['depth']
# profile.name = f'MC (%)'
# test_profile = DesignProfile.profile(self=profile)