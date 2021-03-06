##############################################################################################################
### functions_moea_output_plots.py - python functions used in analyzing and plotting outputs from multi-objective optimization
###     multi-objective optimization
### Project started May 2017, last update Jan 2020
##############################################################################################################
import numpy as np
import pandas as pd
# import statsmodels.formula.api as sm
import matplotlib.pyplot as plt
# from matplotlib.colors import BoundaryNorm
# from matplotlib.ticker import MaxNLocator
import seaborn as sns
# import matplotlib as mpl
from matplotlib import ticker, cm, colors
from matplotlib.lines import Line2D
# from mpl_toolkits.mplot3d import Axes3D
import copy
# import itertools

sns.set_style('ticks')
sns.set_context('paper', font_scale=1.55)

dir_generated_inputs = './../../data/generated_inputs/'
dir_moea_output = './../../data/optimization_output/'
dir_figs = './../../figures/'

cmap_vir = cm.get_cmap('viridis')
col_vir = [cmap_vir(0.1),cmap_vir(0.4),cmap_vir(0.7),cmap_vir(0.85)]
cmap_blues = cm.get_cmap('Blues_r')
col_blues = [cmap_blues(0.1),cmap_blues(0.3),cmap_blues(0.5),cmap_blues(0.8)]
cmap_reds = cm.get_cmap('Reds_r')
col_reds = [cmap_reds(0.1),cmap_reds(0.3),cmap_reds(0.5),cmap_reds(0.8)]
cmap_purples = cm.get_cmap('Purples_r')
col_purples = [cmap_purples(0.1),cmap_purples(0.3),cmap_purples(0.5),cmap_purples(0.8)]
col_brewerQual4 = ['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c']


##################################################################
#### Constants
##################################################################
fixed_cost = 0.914
mean_revenue = 127.80086602479503
mean_net_revenue = mean_revenue * (1 - fixed_cost)




################################################################

#fn for cleaning runtime metrics
def get_metrics(metricfile, hvfile):
  # read data
  df = pd.read_csv(metricfile, sep=' ')
  names = list(df.columns)
  names[0] = names[0].replace('#','')
  df.columns = names

  hv = pd.read_csv(hvfile, sep=' ', header=None)
  df['Hypervolume'] /= hv.iloc[0,0]
  return df






#########################################################################
###### plot nfe vs convergence metrics for num rbfs
### saves plot, no return. ####
# ##########################################################################
def plot_metrics(dir_figs, metrics, nrbfs, nseed, fe_grid, fig_format):
  ### plot moea convergence metrics for different number RBFs
  fig = plt.figure(figsize=(6,8))
  gs1 = fig.add_gridspec(nrows=3, ncols=1, left=0, right=1, wspace=0.1, hspace=0.1)

  ### hypervolume
  ax = fig.add_subplot(gs1[0,0])
  ax.annotate('a)', xy=(0.01, 0.89), xycoords='axes fraction')
  col = ['0.8', '#d73027', '0.65', '0.5','0.35',  '0.2']
  for c, d in enumerate(nrbfs):
    for s in range(nseed):
      hv = metrics[str(d) + 'rbf'][s]['Hypervolume'].values
      hv = np.insert(hv, 0, 0)
      if s < nseed-1:
        ax.plot(fe_grid/1000, hv, c=col[c], alpha=1, zorder=9 - abs(d - 2))
      else:
        if c==0:
          l0, =  ax.plot(fe_grid/1000, hv, c=col[c], alpha=1, zorder=9 - abs(d - 2))
        elif c==1:
          l1, =  ax.plot(fe_grid/1000, hv, c=col[c], alpha=1, zorder=9 - abs(d - 2))
        elif c==2:
          l2, =  ax.plot(fe_grid/1000, hv, c=col[c], alpha=1, zorder=9 - abs(d - 2))
        elif c==3:
          l3, =  ax.plot(fe_grid/1000, hv, c=col[c], alpha=1, zorder=9 - abs(d - 2))
        elif c==4:
          l4, =  ax.plot(fe_grid/1000, hv, c=col[c], alpha=1, zorder=9 - abs(d - 2))
        elif c==5:
          l5, =  ax.plot(fe_grid/1000, hv, c=col[c], alpha=1, zorder=9 - abs(d - 2))
  ax.set_ylim([0.8,1])
  ax.set_xticklabels([])
  ax.set_ylabel('Hypervolume\n' + r'$\rightarrow$')

  ### Additive Epsilon Indicator
  ax = fig.add_subplot(gs1[1,0])
  ax.annotate('b)', xy=(0.01, 0.89), xycoords='axes fraction')
  for c, d in enumerate(nrbfs):
    for s in range(nseed):
      hv = metrics[str(d) + 'rbf'][s]['EpsilonIndicator'].values
      hv = np.insert(hv, 0, 0)
      ax.plot(fe_grid/1000, hv, c=col[c], alpha=1, zorder=9 - abs(d - 2))
  ax.set_ylim([0,0.3])
  ax.set_xticklabels([])
  ax.set_ylabel('Epsilon\nIndicator\n' + r'$\leftarrow$')

  ### Generational Distance
  ax = fig.add_subplot(gs1[2,0])
  ax.annotate('c)', xy=(0.01, 0.89), xycoords='axes fraction')
  for c, d in enumerate(nrbfs):
    for s in range(nseed):
      hv = metrics[str(d) + 'rbf'][s]['GenerationalDistance'].values
      hv = np.insert(hv, 0, 0)
      ax.plot(fe_grid/1000, hv, c=col[c], alpha=1, zorder=9 - abs(d - 2))
  ax.set_ylim([0,0.007])
  ax.set_xlabel('Function Evaluations')
  ax.set_ylabel('Generational\nDistance\n' + r'$\leftarrow$')

  ### add legend & save
  ax.legend([l0, l1, l2, l3, l4, l5], ['1','2','3','4','8','12'], title='Number of RBFs', ncol=6, bbox_to_anchor=(1.02,-0.35), title_fontsize=14)
  plt.savefig(dir_figs + 'compareRbfs.' + fig_format, bbox_inches='tight', dpi=500)

  return







#fn for getting/cleaning solution set data
def get_set(file, nobj, ncon, has_dv = True, has_constraint = True, sort = False):
  # read data
  df = pd.read_csv(file, sep=' ', header=None).dropna(axis=1)
  if (has_dv == True):
    ndv = df.shape[1] - nobj - ncon
  else:
    ndv = 0
  # negate negative objectives
  df.iloc[:, ndv] *= -1
  # get colnames
  if (has_dv == True):
    names = np.array(['dv1'])
    for i in range(2, ndv + 1):
      names = np.append(names, 'dv' + str(i))
    names = np.append(names, 'annRev')
  else:
    names = np.array(['annRev'])
  names = np.append(names, 'maxDebt')
  if (nobj > 2):
    names = np.append(names, 'maxComplex')
    names = np.append(names, 'maxFund')
  if (has_constraint == True):
    names = np.append(names, 'constraint')
  df.columns = names
  # sort based on objective values
  if (sort == True):
    if (nobj == 4):
      df = df.sort_values(by=list(df.columns[-5:-1])).reset_index(drop=True)
    else:
      df = df.sort_values(by=list(df.columns[-5:-1])).reset_index(drop=True)
  return df, ndv



# ### fn to get topsis relative distances for each solution in each solution set, for dynamic vs static comparison
def topsis_dynstat(dfs):
  # dfs = [ref_dps_2obj_retest, ref_2dv_2obj_retest, ref_dps_4obj_retest, ref_2dv_4obj_retest]
  range_objs = {}
  for n,d in enumerate(dfs):
    range_objs[n] = {}
    for o in ['annRev', 'maxDebt', 'maxComplex', 'maxFund']:
      ### normalize objective values (Eqn 2.1** in Roszkowska 2011)
      range_objs[n][o] = [d[o].min(), d[o].max()]
  for n, d in enumerate(dfs):
    for o in ['annRev', 'maxDebt', 'maxComplex', 'maxFund']:
      d[o + 'Norm'] = (d[o] - range_objs[n][o][0]) / (range_objs[n][o][1] - range_objs[n][o][0])
    d['annRevNorm'] = 1 - d['annRevNorm']

    ### calculate L2 distance from positive (0,0,0,0) & negative (1,1,1,1) ideal solutions (Eqn 2.5/2.6 in Roszkowska 2011)
    d['L2_positive_2obj'] = np.sqrt(d['annRevNorm'] **2 + d['maxDebtNorm'] **2)
    d['L2_positive_4obj'] = np.sqrt(d['annRevNorm'] **2 + d['maxDebtNorm'] **2 + d['maxComplexNorm'] **2 + d['maxFundNorm'] **2)
    d['L2_negative_2obj'] = np.sqrt((1 - d['annRevNorm']) **2 + (1 - d['maxDebtNorm']) **2)
    d['L2_negative_4obj'] = np.sqrt((1 - d['annRevNorm']) **2 + (1 - d['maxDebtNorm']) **2 + (1 - d['maxComplexNorm']) **2 + (1 - d['maxFundNorm']) **2)

    ### calculate relative closeness of positive ideal solutions (Eqn 2.7 in Roszkowska 2011)
    d['relCloseness_2obj'] = d['L2_negative_2obj'] / (d['L2_negative_2obj'] + d['L2_positive_2obj'])
    d['relCloseness_4obj'] = d['L2_negative_4obj'] / (d['L2_negative_4obj'] + d['L2_positive_4obj'])

  return dfs


# ### fn to get topsis relative distances for each solution in each solution set, for subproblems
def topsis_subproblems(problems, paretos, pareto_cols):
  range_objs = {}
  for k in problems:
    d = paretos[k]
    range_objs[k] = {}
    ### normalize objective values (Eqn 2.1** in Roszkowska 2011)
    for o in pareto_cols[k]:
      range_objs[k][o] = [d[o].min(), d[o].max()]
      d[o + 'Norm'] = (d[o] - range_objs[k][o][0]) / (range_objs[k][o][1] - range_objs[k][o][0])
    if ('annRev' in pareto_cols[k]):
      d['annRevNorm'] = 1 - d['annRevNorm']
    ### calculate L2 distance from positive (0,0,0,0) & negative (1,1,1,1) ideal solutions (Eqn 2.5/2.6 in Roszkowska 2011)
    d['L2_positive'] = 0
    d['L2_negative'] = 0
    if ('annRev' in pareto_cols[k]):
      d['L2_positive']  += d['annRevNorm'] ** 2
      d['L2_negative']  += (1 - d['annRevNorm']) ** 2
    if ('maxDebt' in pareto_cols[k]):
      d['L2_positive']  += d['maxDebtNorm'] ** 2
      d['L2_negative']  += (1 - d['maxDebtNorm']) ** 2
    if ('maxComplex' in pareto_cols[k]):
      d['L2_positive']  += d['maxComplexNorm'] ** 2
      d['L2_negative']  += (1 - d['maxComplexNorm']) ** 2
    if ('maxFund' in pareto_cols[k]):
      d['L2_positive']  += d['maxFundNorm'] ** 2
      d['L2_negative']  += (1 - d['maxFundNorm']) ** 2
    d['L2_positive'] = np.sqrt(d['L2_positive'] )
    d['L2_negative'] = np.sqrt(d['L2_negative'] )
    ### calculate relative closeness of positive ideal solutions (Eqn 2.7 in Roszkowska 2011)
    d['relCloseness'] = d['L2_negative'] / (d['L2_negative'] + d['L2_positive'])

  return paretos



# ### fn to plot 2-objective solution sets for dynamic & static formulations
def plot_2obj_dynstat(ref_2dv_2obj_retest, ref_dps_2obj_retest, lims2d, fig_format):
  fig = plt.figure()
  ax = fig.add_subplot(111)

  ### get best compromise points from topsis relative closeness
  min_dist = [np.where(ref_2dv_2obj_retest.relCloseness_2obj == ref_2dv_2obj_retest.relCloseness_2obj.max())[0][0],
              np.where(ref_dps_2obj_retest.relCloseness_2obj == ref_dps_2obj_retest.relCloseness_2obj.max())[0][0]]
  x_min_dist = [ref_2dv_2obj_retest.maxDebt.iloc[min_dist[0]], ref_dps_2obj_retest.maxDebt.iloc[min_dist[1]]]
  y_min_dist = [ref_2dv_2obj_retest.annRev.iloc[min_dist[0]], ref_dps_2obj_retest.annRev.iloc[min_dist[1]]]

  ### plot figure
  ys = ref_2dv_2obj_retest.annRev
  xs = ref_2dv_2obj_retest.maxDebt
  p1 = ax.scatter(xs,ys, c=col_reds[2], marker='^', alpha=1, s=60)
  p1 = ax.scatter(x_min_dist[0], y_min_dist[0], c=col_reds[2], edgecolors='k', lw=1.5, marker='^', alpha=1, s=60)
  ys = ref_dps_2obj_retest.annRev
  xs = ref_dps_2obj_retest.maxDebt
  p1 = ax.scatter(xs, ys, c=col_blues[2], marker='v', alpha=1, s=60)
  p1 = ax.scatter(x_min_dist[1], y_min_dist[1], c=col_blues[2], edgecolors='k', lw=1.5, marker='v', alpha=1, s=60)
  plt.xticks([0,10,20,30])
  plt.yticks([9.5,10,10.5,11])
  plt.tick_params(length=3)
  plt.plot([0],[mean_net_revenue],marker='*',ms=15,c='k', zorder=2)
  ax.axhline(mean_net_revenue, color='0.5', ls=':', zorder=1)
  ax.axvline(0, color='0.5', ls=':', zorder=1)
  plt.xlim(lims2d['maxDebt'])
  plt.ylim(lims2d['annRev'])
  plt.savefig(dir_figs + 'compare2dvDps_2objForm_2objView.' + fig_format, bbox_inches='tight', dpi=500)

  ### output for Table 2
  columns = [['annRev', 'maxDebt', 'maxComplex', 'maxFund']]
  subset = ref_2dv_2obj_retest.iloc[min_dist[0], :]
  table2 = pd.DataFrame({'formulation': '2obj_static', 'annRev': subset['annRev'], 'maxDebt': subset['maxDebt'], 
                      'maxComplex': subset['maxComplex'], 'maxFund': subset['maxFund']}, index=[0])

  subset = ref_dps_2obj_retest.iloc[min_dist[1], :]
  table2 = table2.append(pd.DataFrame({'formulation': '2obj_dynamic', 'annRev': subset['annRev'], 'maxDebt': subset['maxDebt'], 
                                  'maxComplex': subset['maxComplex'], 'maxFund': subset['maxFund']}, index=[1]))

  return table2



# ### fn to plot 4-objective solution sets for dynamic & static formulations
def plot_4obj_dynstat(ref_2dv_4obj_retest, ref_dps_4obj_retest, lims3d, fig_format):
  fig = plt.figure()
  ax = fig.add_subplot(1,1,1, projection='3d')
  # min_dist = [np.where(ref_dps_4obj_retest.relCloseness_4obj == ref_dps_4obj_retest.relCloseness_4obj.max())[0][0],
  #             np.where(ref_2dv_4obj_retest.relCloseness_4obj == ref_2dv_4obj_retest.relCloseness_4obj.max())[0][0]]
  # z_min_dist = [ref_dps_4obj_retest.annRev.iloc[min_dist[0]], ref_2dv_4obj_retest.annRev.iloc[min_dist[1]]]
  # y_min_dist = [ref_dps_4obj_retest.maxDebt.iloc[min_dist[0]], ref_2dv_4obj_retest.maxDebt.iloc[min_dist[1]]]
  # x_min_dist = [ref_dps_4obj_retest.maxComplex.iloc[min_dist[0]], ref_2dv_4obj_retest.maxComplex.iloc[min_dist[1]]]
  # s_min_dist = [ref_dps_4obj_retest.maxFund.iloc[min_dist[0]], ref_2dv_4obj_retest.maxFund.iloc[min_dist[1]]]
  # zs = ref_dps_4obj_retest.annRev.drop(min_dist[0])
  # ys = ref_dps_4obj_retest.maxDebt.drop(min_dist[0])
  # xs = ref_dps_4obj_retest.maxComplex.drop(min_dist[0])
  # ss = 20 + 1.3*ref_dps_4obj_retest.maxFund.drop(min_dist[0])
  # p1 = ax.scatter(xs, ys, zs, s=ss, marker='v', alpha=0.6, c=col_blues[2])
  # p1 = ax.scatter(x_min_dist[0], y_min_dist[0], z_min_dist[0], s=s_min_dist[0], marker='v', alpha=1, c=col_blues[0])
  # zs = ref_2dv_4obj_retest.annRev.drop(min_dist[1])
  # ys = ref_2dv_4obj_retest.maxDebt.drop(min_dist[1])
  # xs = ref_2dv_4obj_retest.maxComplex.drop(min_dist[1])
  # ss = 20 + 1.3*ref_2dv_4obj_retest.maxFund.drop(min_dist[1])
  # p1 = ax.scatter(xs, ys, zs, s=ss, marker='^',alpha=0.6, c=col_reds[2])
  # p1 = ax.scatter(x_min_dist[1], y_min_dist[1], z_min_dist[1], s=s_min_dist[1], marker='^', alpha=1, c=col_reds[0])
  zs = ref_dps_4obj_retest.annRev
  ys = ref_dps_4obj_retest.maxDebt
  xs = ref_dps_4obj_retest.maxComplex
  ss = 20 + 1.3*ref_dps_4obj_retest.maxFund
  p1 = ax.scatter(xs, ys, zs, s=ss, marker='v', alpha=0.6, c=col_blues[2])
  zs = ref_2dv_4obj_retest.annRev
  ys = ref_2dv_4obj_retest.maxDebt
  xs = ref_2dv_4obj_retest.maxComplex
  ss = 20 + 1.3*ref_2dv_4obj_retest.maxFund
  p1 = ax.scatter(xs, ys, zs, s=ss, marker='^',alpha=0.6, c=col_reds[2])
  ax.set_yticks([12, 24, 36])
  ax.set_zticks([9.5,10,10.5,11])
  ax.set_xticks([0,0.25,0.5,0.75,1])
  ax.view_init(elev=20, azim =-45)
  ax.plot([0.01],[0.01],[mean_net_revenue+0.05],marker='*',ms=15,c='k')
  ax.set_xlim(lims3d['maxComplex'])
  ax.set_ylim(lims3d['maxDebt'])
  ax.set_zlim(lims3d['annRev'])
  plt.savefig(dir_figs + 'compare2dvDps_4objForm_4objView.' + fig_format, bbox_inches='tight', figsize=(4.5,8), dpi=500)

  return




# ### fn to plot min & max marker sizes for 3d 4-objective plot legend
def plot_4obj_markersize(ref_2dv_4obj_retest, ref_dps_4obj_retest, lims3d, fig_format):
  
  fig = plt.figure()
  ax = fig.add_subplot(1,1,1, projection='3d')
  min_F = min(ref_dps_4obj_retest.maxFund.min(), ref_2dv_4obj_retest.maxFund.max())
  max_F = max(ref_dps_4obj_retest.maxFund.max(), ref_2dv_4obj_retest.maxFund.max())
  min_s = 20 + 1.3 * min_F
  max_s = 20 + 1.3 * max_F

  zs = ref_2dv_4obj_retest.annRev
  ys = ref_2dv_4obj_retest.maxDebt
  xs = ref_2dv_4obj_retest.maxComplex
  ss = 20 + 1.3*ref_2dv_4obj_retest.maxFund
  p1 = ax.scatter(xs[0], ys[0], zs[0], s=min_s, marker='v',alpha=0.6, c='0.5') 
  p1 = ax.scatter(xs[100], ys[100], zs[100], s=max_s, marker='v',alpha=0.6, c='0.5') 
  ax.set_yticks([12, 24, 36])
  ax.set_zticks([9.5,10,10.5,11])
  ax.set_xticks([0,0.25,0.5,0.75,1])
  ax.view_init(elev=20, azim =-45)
  ax.plot([0.01],[0.01],[mean_net_revenue+0.05],marker='*',ms=15,c='k')
  ax.set_xlim(lims3d['maxComplex'])
  ax.set_ylim(lims3d['maxDebt'])
  ax.set_zlim(lims3d['annRev'])
  plt.title('min: ' + str(min_F) + ', max: ' + str(max_F))
  plt.savefig(dir_figs + 'compare2dvDps_4objForm_4objView_size.' + fig_format, bbox_inches='tight', figsize=(4.5,8), dpi=500)




# ### fn to plot performance of solution sets from all sub-problems
def plot_subproblems(ref_dps_4obj_retest, lims3d, ref_dps_2obj_retest, lims2d, fig_format):
  ### get subproblem pareto fronts
  subproblems = ['123','124','134','234','12','13','14','23','24','34']
  paretos = {}
  paretos['1234'] = ref_dps_4obj_retest.copy()
  for s in subproblems:
      ### get line numbers that are non-dominated in each sub-problem
      linenums = np.loadtxt(dir_moea_output + '4obj_2rbf_moreSeeds/DPS_4obj_2rbf_' + s + '.linefile', skiprows=1)
      try:
          linenums = [int(l) - 1 for l in linenums]
      except:
          linenums = [int(linenums) - 1]
      paretos[s] = ref_dps_4obj_retest.iloc[linenums, :]

  ### objectives for each sub-problem
  subproblems_with_conflicts = ['1234','123','124','234','12','23','24']
  pareto_cols = {}
  pareto_cols['1234'] = ['annRev', 'maxDebt', 'maxComplex', 'maxFund']
  pareto_cols['123'] = ['annRev', 'maxDebt', 'maxComplex']
  pareto_cols['124'] = ['annRev', 'maxDebt', 'maxFund']
  pareto_cols['234'] = ['maxDebt', 'maxComplex', 'maxFund']
  pareto_cols['12'] = ['annRev', 'maxDebt']
  pareto_cols['23'] = ['maxDebt', 'maxComplex']
  pareto_cols['24'] = ['maxDebt', 'maxFund']

  ### plot 2obj pareto fronts from 2obj and 4obj formualtions
  fig = plt.figure()
  ax = fig.add_subplot(111)
  ys = paretos['12'].annRev
  xs = paretos['12'].maxDebt
  p1 = ax.scatter(xs,ys, c=col_blues[2], marker='^', alpha=1, s=60)
  ys = ref_dps_2obj_retest.annRev
  xs = ref_dps_2obj_retest.maxDebt
  p1 = ax.scatter(xs, ys, c=col_reds[2], marker='v', alpha=1, s=60)
  plt.xticks([0,10,20,30])
  plt.yticks([9.5,10,10.5,11])
  plt.tick_params(length=3)
  plt.plot([0],[mean_net_revenue],marker='*',ms=15,c='k', zorder=2)
  ax.axhline(mean_net_revenue, color='0.5', ls=':', zorder=1)
  ax.axvline(0, color='0.5', ls=':', zorder=1)
  plt.xlim(lims2d['maxDebt'])
  plt.ylim(lims2d['annRev'])
  plt.savefig(dir_figs + 'compareObjFormulations_2objProj.' + fig_format, bbox_inches='tight', dpi=500)

  ### plot 4obj pareto fronts from 2obj and 4obj formualtions
  fig = plt.figure()
  ax = fig.add_subplot(1,1,1, projection='3d')
  zs = ref_dps_2obj_retest.annRev
  ys = ref_dps_2obj_retest.maxDebt
  xs = ref_dps_2obj_retest.maxComplex
  ss = 20 + 1.3*ref_dps_2obj_retest.maxFund
  p1 = ax.scatter(xs, ys, zs, s=ss, marker='v', alpha=0.6, c=col_reds[2])
  zs = paretos['12'].annRev
  ys = paretos['12'].maxDebt
  xs = paretos['12'].maxComplex
  ss = 20 + 1.3*paretos['12'].maxFund
  p1 = ax.scatter(xs, ys, zs, s=ss, marker='^',alpha=0.6, c=col_blues[2])
  ax.set_yticks([12, 24, 36])
  ax.set_zticks([9.5,10,10.5,11])
  ax.set_xticks([0,0.25,0.5,0.75,1])
  ax.view_init(elev=20, azim =-45)
  ax.plot([0.01],[0.01],[mean_net_revenue+0.05],marker='*',ms=15,c='k')
  ax.set_xlim(lims3d['maxComplex'])
  ax.set_ylim(lims3d['maxDebt'])
  ax.set_zlim(lims3d['annRev'])
  plt.savefig(dir_figs + 'compareObjFormulations_4objProj.' + fig_format, bbox_inches='tight', dpi=500)

  ### plot pareto fronts for each subproblem
  fig = plt.figure()
  baseline = paretos['1234'].copy()
  ax = fig.add_subplot(1,1,1, projection='3d')
  subprob = paretos['12'].copy()
  baseline = baseline.drop(subprob.index, errors='ignore')

  ### figure with sub-problem solution sets
  zs = subprob.annRev
  ys = subprob.maxDebt
  xs = subprob.maxComplex
  ss = 20 + 1.3 * subprob.maxFund
  p1 = ax.scatter(xs, ys, zs, s=ss, marker='v', alpha=1, c=[col_blues[2]])
  subprob = paretos['23'].copy()
  baseline = baseline.drop(subprob.index, errors='ignore')
  zs = subprob.annRev
  ys = subprob.maxDebt
  xs = subprob.maxComplex
  ss = 20 + 1.3 * subprob.maxFund
  p1 = ax.scatter(xs, ys, zs, s=ss, marker='<', alpha=1, c=[col_reds[2]])
  subprob = paretos['24'].copy()
  baseline = baseline.drop(subprob.index, errors='ignore')
  zs = subprob.annRev
  ys = subprob.maxDebt
  xs = subprob.maxComplex
  ss = 20 + 1.3 * subprob.maxFund
  p1 = ax.scatter(xs, ys, zs, s=ss, marker='>', alpha=1, c=[col_purples[2]])
  subprob = paretos['13'].copy()
  baseline = baseline.drop(subprob.index, errors='ignore')
  zs = subprob.annRev
  ys = subprob.maxDebt
  xs = subprob.maxComplex
  ss = 20 + 1.3 * subprob.maxFund
  p1 = ax.scatter(xs, ys, zs, s=ss, marker='^', alpha=1, c='0.4')
  subprob = paretos['14'].copy()
  baseline = baseline.drop(subprob.index, errors='ignore')
  zs = subprob.annRev
  ys = subprob.maxDebt
  xs = subprob.maxComplex
  ss = 20 + 1.3 * subprob.maxFund
  p1 = ax.scatter(xs, ys, zs, s=ss, marker='^', alpha=1, c='0.4')
  subprob = paretos['34'].copy()
  baseline = baseline.drop(subprob.index, errors='ignore')
  zs = subprob.annRev
  ys = subprob.maxDebt
  xs = subprob.maxComplex
  ss = 20 + 1.3 * subprob.maxFund
  p1 = ax.scatter(xs, ys, zs, s=ss, marker='^', alpha=1, c='0.4')
  zs = baseline.annRev
  ys = baseline.maxDebt
  xs = baseline.maxComplex
  ss = 20 + 1.3*baseline.maxFund
  p1 = ax.scatter(xs, ys, zs, s=ss, marker='^', alpha=1, c='0.8')
  ax.set_xticks([0,0.25,0.5,0.75])
  ax.set_yticks([12, 24, 36])
  ax.set_zticks([9.5,10,10.5,11])
  ax.view_init(elev=20, azim =-45)
  ax.plot([0.01],[0.01],[mean_net_revenue+0.05],marker='*',ms=15,c='k')
  ax.set_xlim(lims3d['maxComplex'])
  ax.set_ylim(lims3d['maxDebt'])
  ax.set_zlim(lims3d['annRev'])
  plt.savefig(dir_figs + 'compareObjFormulations_2objSub.' + fig_format, bbox_inches='tight', figsize=(4.5,8), dpi=500)

  ### now make figures for 3 3-obj sub-problems with conflicts
  for k in ['123','124','234']:
    fig = plt.figure()
    baseline = paretos['1234'].copy()
    ax = fig.add_subplot(1,1,1, projection='3d')
    subprob = paretos[k].copy()
    baseline = baseline.drop(subprob.index, errors='ignore')
    zs = subprob.annRev
    ys = subprob.maxDebt
    xs = subprob.maxComplex
    ss = 20 + 1.3*subprob.maxFund
    p1 = ax.scatter(xs, ys, zs, s=ss, marker='v', alpha=1, c=[col_blues[2]])
    zs = baseline.annRev
    ys = baseline.maxDebt
    xs = baseline.maxComplex
    ss = 20 + 1.3*baseline.maxFund
    p1 = ax.scatter(xs, ys, zs, s=ss, marker='^', alpha=1, c='0.8')
    ax.set_xticks([0,0.25,0.5,0.75])
    ax.set_yticks([12, 24, 36])
    ax.set_zticks([9.5,10,10.5,11])
    ax.view_init(elev=20, azim =-45)
    ax.plot([0.01],[0.01],[mean_net_revenue+0.05],marker='*',ms=15,c='k')
    ax.set_xlim(lims3d['maxComplex'])
    ax.set_ylim(lims3d['maxDebt'])
    ax.set_zlim(lims3d['annRev'])
    plt.savefig(dir_figs + 'compareObjFormulations_' + k + '.' + fig_format, bbox_inches='tight', figsize=(4.5,8), dpi=500)

  return paretos, pareto_cols





### fn to plot solutions meeting brushing contraints
def plot_4obj_brush(paretos, pareto_cols, constraints, lims3d, fig_format, table2):

  # ### plot policies meeting brushing constraints
  k = '1234_constraint'
  paretos[k] = paretos['1234'].copy()
  pareto_cols[k] = pareto_cols['1234']

  ### set constraints based on user input (annRev, maxDebt, & maxFund should be fractions of mean_net_revenue, maxComplex should be scalar b/w 0 & 1 (or larger than 1 to have no constraint))
  min_annRev = mean_net_revenue * constraints['annRev']
  max_maxDebt = mean_net_revenue * constraints['maxDebt']
  max_maxComplex = constraints['maxComplex']
  max_maxFund = mean_net_revenue * constraints['maxFund']
  brush_annRev = paretos[k].annRev >= min_annRev
  brush_maxDebt = paretos[k].maxDebt <= max_maxDebt
  brush_maxComplex = paretos[k].maxComplex <= max_maxComplex
  brush_maxFund = paretos[k].maxFund <= max_maxFund
  paretos[k] = paretos[k].loc[(brush_annRev & brush_maxDebt & brush_maxComplex & brush_maxFund), :]

  paretos = topsis_subproblems([k], paretos, pareto_cols)
  
  ### figure
  fig = plt.figure()
  baseline = paretos['1234'].copy()
  ax = fig.add_subplot(1, 1, 1, projection='3d')
  subprob = paretos[k].copy()
  baseline = baseline.drop(subprob.index, errors='ignore')
  ind = subprob.index[np.where(subprob.relCloseness == subprob.relCloseness.max())[0][0]]

  ### output for Table 2
  table2 = table2.append(pd.DataFrame({'formulation': '4obj_dynamic_constraints', 'annRev': subprob.annRev.loc[ind], 'maxDebt': subprob.maxDebt.loc[ind], 
                                  'maxComplex': subprob.maxComplex.loc[ind], 'maxFund': subprob.maxFund.loc[ind]}, index=[2]))
  table2.to_csv('../../figures/table2.csv')

  zs = subprob.annRev.loc[ind]
  ys = subprob.maxDebt.loc[ind]
  xs = subprob.maxComplex.loc[ind]
  ss = 20 + 1.3 * subprob.maxFund.loc[ind]
  p1 = ax.scatter(xs, ys, zs, s=ss, marker='v', alpha=1, c=[col_blues[2]], edgecolors='k', lw=1.5)
  zs = subprob.annRev.drop(ind)
  ys = subprob.maxDebt.drop(ind)
  xs = subprob.maxComplex.drop(ind)
  ss = 20 + 1.3 * subprob.maxFund.drop(ind)
  p1 = ax.scatter(xs, ys, zs, s=ss, marker='v', alpha=0.4, c=[col_blues[2]])
  zs = baseline.annRev
  ys = baseline.maxDebt
  xs = baseline.maxComplex
  ss = 20 + 1.3 * baseline.maxFund
  p1 = ax.scatter(xs, ys, zs, s=ss, marker='^', alpha=0.1, c='0.8')
  ax.set_xticks([0,0.25,0.5,0.75])
  ax.set_yticks([12, 24, 36])
  ax.set_zticks([9.5,10,10.5,11])
  ax.view_init(elev=20, azim =-45)
  ax.plot([0.01],[0.01],[mean_net_revenue+0.05],marker='*',ms=15,c='k')
  ax.set_xlim(lims3d['maxComplex'])
  ax.set_ylim(lims3d['maxDebt'])
  ax.set_zlim(lims3d['annRev'])
  plt.savefig(dir_figs + 'compareObjFormulations_' + k + '.' + fig_format, bbox_inches='tight', figsize=(4.5, 8), dpi=500)

  return 












######################## functions for simulating policies ###################################################


##################################################################
#### Constants for simulation, consistent with C++ version used for optimization
##################################################################
DPS_RUN_TYPE = 1          # 0: 2dv version; 1: full DPS with RBFs, maxDebt formulation; 2: full DPS with RBFs, minRev formulation
#BORG_RUN_TYPE 1       # 0: single run no borg; 1: borg run, serial; 2: borg parallel for cluster;
# NUM_YEARS = 20                   #20yr sims
# NUM_SAMPLES = 50000
NUM_DECISIONS_TOTAL = 2           # each year, have to choose value snow contract + adjusted revenue
#NUM_LINES_STOCHASTIC_INPUT 999999    #Input file samp.txt has 1M rows, 6 cols.
#NUM_VARIABLES_STOCHASTIC_INPUT 6            #6 cols in input: swe,powIndex,revRetail,revWholesale,sswp,pswp
#INDEX_STOCHASTIC_REVENUE 2   # 2 = revRetail, 3 = revWholesale
#INDEX_STOCHASTIC_SNOW_PAYOUT 4    # 4 = sswp
#INDEX_STOCHASTIC_POWER_INDEX 1  # 1 = power index
#if INDEX_STOCHASTIC_REVENUE == 2
MEAN_REVENUE = mean_revenue    # mean revenue in absense of any financial risk mgmt. Make sure this is consistent with current input HHSamp revenue column.
#elif INDEX_STOCHASTIC_REVENUE == 3
#MEAN_REVENUE  70.08967184742373     # mean revenue in absense of any financial risk mgmt. Make sure this is consistent with current input HHSamp revenue column.
#endif
NORMALIZE_SNOW_CONTRACT_SIZE = 4.0
NORMALIZE_REVENUE = 250.0
NORMALIZE_FUND = 150.0
NORMALIZE_POWER_PRICE = 350.0
NORMALIZE_SWE = 150.0
#BUFFER_MAX_SIZE 5000
EPS = 0.0000000000001
NUM_OBJECTIVES = 4
#EPS_ANNREV 0.075
#EPS_MAXDEBT 0.225
#EPS_MINREV 0.225
#EPS_MAXCOMPLEXITY 0.05
#EPS_MAXFUND 0.225
#if DPS_RUN_TYPE<2
#NUM_CONSTRAINTS 1
#else
#NUM_CONSTRAINTS 0
#endif
#EPS_CONS1 0.05
NUM_RBF = 2       # number of radial basis functions
SHARED_RBFS = 1     # 1 = 1 rbf shared between hedge and withdrawal policies. 0 = separate rbf for each. 2 = rbf for hedge, and 2dv formulation for withdrawal.
if (SHARED_RBFS == 2):
  NUM_INPUTS_RBF = 3    # inputs: fund balance, debt, power index
else:
  NUM_INPUTS_RBF = 4    # inputs: fund balance, debt, power index, rev+hedge cash flow
if (DPS_RUN_TYPE > 0):
  if (SHARED_RBFS == 0):
    NUM_DV = (2 * NUM_DECISIONS_TOTAL * NUM_RBF * NUM_INPUTS_RBF) + (NUM_DECISIONS_TOTAL * (NUM_RBF + 2))
  elif (SHARED_RBFS == 1):
    NUM_DV = (2 * NUM_RBF * NUM_INPUTS_RBF) + (NUM_DECISIONS_TOTAL * (NUM_RBF + 2))
  else:
    NUM_DV = (2 * NUM_RBF * NUM_INPUTS_RBF) + (NUM_DECISIONS_TOTAL * 2) + NUM_RBF
else:
  NUM_DV = 2
# MIN_SNOW_CONTRACT= 0.05          # DPS_RUN_TYPE==0 only: if contract slope dv < $0.05M/inch, act as if 0.
# MIN_MAX_FUND= 0.05               # DPS_RUN_TYPE==0 only: if max fund dv < $0.05M, act as if 0.
#NUM_PARAM 6         # cost_fraction, discount_rate, delta_interest_fund, delta_interest_debt, lambda, lambda_prem_shift
#NUM_PARAM_SAMPLES 1  # number of LHC samples in param file. Last line is values for SFPUC, Oct 2016.

fixed_cost = 0.914
delta = 0.4
Delta_fund = -1.73
Delta_debt = 1
# lam = 0.25
# lam_prem_shift = 0

# get financial params
# discount_rate = 1 / (delta/100 + 1)
interest_fund = (Delta_fund + delta)/100 + 1
interest_debt = (Delta_debt + delta)/100 + 1
# discount_factor = discount_rate ** np.arange(1, NUM_YEARS+1)
# discount_normalization = 1 / np.sum(discount_factor)



# get decision variables to use for simulation
def get_dvs(dvs):
    global dv_d, dv_c, dv_b, dv_w, dv_a
    dv_d = np.zeros(NUM_DECISIONS_TOTAL)
    if (SHARED_RBFS == 0):
      dv_c = np.zeros(NUM_RBF * NUM_INPUTS_RBF * NUM_DECISIONS_TOTAL)
      dv_b = np.zeros(NUM_RBF * NUM_INPUTS_RBF * NUM_DECISIONS_TOTAL)
    else:
      dv_c = np.zeros(NUM_RBF * NUM_INPUTS_RBF)
      dv_b = np.zeros(NUM_RBF * NUM_INPUTS_RBF)
    if (SHARED_RBFS == 2):
      dv_w = np.zeros(NUM_RBF)
    else:
      dv_w = np.zeros(NUM_RBF * NUM_DECISIONS_TOTAL)
    dv_a = np.zeros(NUM_DECISIONS_TOTAL)
    objDPS = np.zeros(NUM_OBJECTIVES)
    for i in range(len(dv_d)):
        dv_d[i] = dvs[i]
    for i in range(len(dv_c)):
        dv_c[i] = dvs[i + len(dv_d)]
    for i in range(len(dv_b)):
        dv_b[i] = max(dvs[i + len(dv_d) + len(dv_c)],EPS)
    for i in range(len(dv_w)):
        dv_w[i] = dvs[i + len(dv_d) + len(dv_c) + len(dv_b)]
    for i in range(len(dv_a)):
        dv_a[i] = dvs[i + len(dv_d) + len(dv_c) + len(dv_b) + len(dv_w)]
    for i in range(NUM_OBJECTIVES):
        objDPS[i] = dvs[i + len(dv_d) + len(dv_c) + len(dv_b) + len(dv_w) + len(dv_a)]
    # normalize weights
    for j in range(NUM_DECISIONS_TOTAL):
        dum = np.sum(dv_w[(j * NUM_RBF):((j + 1) * NUM_RBF)])
        if dum > 0:
          dv_w[(j * NUM_RBF):((j + 1) * NUM_RBF)] = dv_w[(j * NUM_RBF):((j + 1) * NUM_RBF)] / dum
    return (dv_d, dv_c, dv_b, dv_w, dv_a)




### simulate hydro-financial model
def simulate(revenue, payout, power, policy=-1, dps_run_type=-1):
  ### default simulation assumes dps simulation
  if dps_run_type < 0:
    ny = len(revenue) - 1
    net_rev = revenue - MEAN_REVENUE * fixed_cost
    fund = np.zeros(ny + 1)
    debt = np.zeros(ny + 1)
    final_cashflow = np.zeros(ny)
    withdrawal = np.zeros(ny)
    value_snow_contract = np.zeros(ny)
    cash_in = np.zeros(ny)
    for i in range(ny):
      value_snow_contract[i] = policy_hedge_dps(fund[i], debt[i], power[i])
      net_payout_snow_contract = value_snow_contract[i] * payout[i+1]
      cash_in[i] = net_rev[i+1] + net_payout_snow_contract - debt[i] * interest_debt
      withdrawal[i] = policy_withdrawal_dps(fund[i]*interest_fund, debt[i]*interest_debt, power[i+1], cash_in[i])
      final_cashflow[i] = cash_in[i] + withdrawal[i]
      fund[i+1] = fund[i]*interest_fund - withdrawal[i]
      if (final_cashflow[i] < -EPS):
        debt[i+1] = -final_cashflow[i]
        final_cashflow[i] = 0
  else:
    ny = len(revenue) - 1
    net_rev = revenue - MEAN_REVENUE * fixed_cost
    fund = np.zeros(ny + 1)
    debt = np.zeros(ny + 1)
    final_cashflow = np.zeros(ny)
    withdrawal = np.zeros(ny)
    value_snow_contract = np.zeros(ny)
    cash_in = np.zeros(ny)

    for i in range(ny):
      if dps_run_type == 0:
        max_fund = policy.dv1
        value_snow_contract[i] = policy.dv2
      else:
        value_snow_contract[i] = policy_hedge_dps(fund[i], debt[i], power[i])
      net_payout_snow_contract = value_snow_contract[i] * payout[i+1]
      cash_in[i] = net_rev[i+1] + net_payout_snow_contract - debt[i] * interest_debt
      if dps_run_type == 0:
        # rule for withdrawal (or deposit), after growing fund at interestFund from last year
        final_cashflow[i] = policy_cashflow_post_withdrawal_2dv(fund[i] * interest_fund, cash_in[i], 0, max_fund)
        withdrawal[i] = final_cashflow[i] - cash_in[i]
      else:
        withdrawal[i] = policy_withdrawal_dps(fund[i]*interest_fund, debt[i]*interest_debt, power[i+1], cash_in[i])
        final_cashflow[i] = cash_in[i] + withdrawal[i]
      fund[i+1] = fund[i]*interest_fund - withdrawal[i]
      if (final_cashflow[i] < -EPS):
        debt[i+1] = -final_cashflow[i]
        final_cashflow[i] = 0

  return (fund[:-1], fund[:-1]*interest_fund, debt[:-1], debt[:-1]*interest_debt, power[:-1], power[1:], cash_in, value_snow_contract, withdrawal, final_cashflow)





### get hedging contract slope each year from dps policy based on current conditions
def policy_hedge_dps(f_fund_balance, f_debt, f_power_price_index, useinrbf_fund_hedge=1, useinrbf_debt_hedge=1, useinrbf_power_hedge=1):
  decision_order = 0
  value = 0
  for i in range(NUM_RBF):
    # sum RBFs
    if (SHARED_RBFS == 1):
      arg_exp = -((f_fund_balance * useinrbf_fund_hedge / NORMALIZE_FUND - dv_c[NUM_INPUTS_RBF * i]) ** 2) \
                 / (dv_b[NUM_INPUTS_RBF * i]) ** 2
      arg_exp += -((f_debt * useinrbf_debt_hedge / NORMALIZE_FUND - dv_c[NUM_INPUTS_RBF * i + 1]) ** 2) \
                 / (dv_b[NUM_INPUTS_RBF * i + 1]) ** 2
      arg_exp += -((f_power_price_index * useinrbf_power_hedge / NORMALIZE_POWER_PRICE - dv_c[NUM_INPUTS_RBF * i + 2]) ** 2) \
                 / (dv_b[NUM_INPUTS_RBF * i + 2]) ** 2
    else:
      arg_exp = -((f_fund_balance * useinrbf_fund_hedge / NORMALIZE_FUND - dv_c[(decision_order * NUM_INPUTS_RBF * NUM_RBF) + NUM_INPUTS_RBF * i]) ** 2) \
                 / (dv_b[(decision_order * NUM_INPUTS_RBF * NUM_RBF) + NUM_INPUTS_RBF * i]) ** 2
      arg_exp += -((f_debt * useinrbf_debt_hedge / NORMALIZE_FUND - dv_c[(decision_order * NUM_INPUTS_RBF * NUM_RBF) + NUM_INPUTS_RBF * i + 1]) ** 2) \
                 / (dv_b[(decision_order * NUM_INPUTS_RBF * NUM_RBF) + NUM_INPUTS_RBF * i + 1]) ** 2
      arg_exp += -((f_power_price_index * useinrbf_power_hedge / NORMALIZE_POWER_PRICE - dv_c[(decision_order * NUM_INPUTS_RBF * NUM_RBF) + NUM_INPUTS_RBF * i + 2]) ** 2) \
                 / (dv_b[(decision_order * NUM_INPUTS_RBF * NUM_RBF) + NUM_INPUTS_RBF * i + 2]) ** 2
    value += dv_w[decision_order * NUM_RBF + i] * np.exp(arg_exp)
  # add constant term & scale to [0, NORMALIZE_SNOW_CONTRACT_SIZE]
  value = max(min((value + dv_a[decision_order]) * NORMALIZE_SNOW_CONTRACT_SIZE, NORMALIZE_SNOW_CONTRACT_SIZE), 0)
  # enforce minimum contract size
  if (value < dv_d[decision_order] * NORMALIZE_SNOW_CONTRACT_SIZE):
    value = 0

  return (value)





### get withdrawal/deposit each year from dps policy based on current conditions
def policy_withdrawal_dps(f_fund_balance, f_debt, f_power_price_index, f_cash_in, useinrbf_fund_withdrawal=1, useinrbf_debt_withdrawal=1, useinrbf_power_withdrawal=1, useinrbf_cashin_withdrawal=1):
  decision_order = 1
  cash_out = 0
  for i in range(NUM_RBF):
    # sum RBFs
    if (SHARED_RBFS == 0):
      arg_exp = -((f_fund_balance * useinrbf_fund_withdrawal / NORMALIZE_FUND - dv_c[(decision_order * NUM_INPUTS_RBF * NUM_RBF) + NUM_INPUTS_RBF * i]) ** 2) \
                    / (dv_b[(decision_order * NUM_INPUTS_RBF * NUM_RBF) + NUM_INPUTS_RBF * i]) ** 2\
                -((f_debt * useinrbf_debt_withdrawal / NORMALIZE_FUND - dv_c[(decision_order * NUM_INPUTS_RBF * NUM_RBF) + NUM_INPUTS_RBF * i + 1]) ** 2) \
                    / (dv_b[(decision_order * NUM_INPUTS_RBF * NUM_RBF) + NUM_INPUTS_RBF * i + 1]) ** 2\
                -((f_power_price_index * useinrbf_power_withdrawal / NORMALIZE_POWER_PRICE - dv_c[(decision_order * NUM_INPUTS_RBF * NUM_RBF) + NUM_INPUTS_RBF * i + 2]) ** 2) \
                    / (dv_b[(decision_order * NUM_INPUTS_RBF * NUM_RBF) + NUM_INPUTS_RBF * i + 2]) ** 2\
                -(((f_cash_in * useinrbf_cashin_withdrawal + NORMALIZE_REVENUE) / (2 * NORMALIZE_REVENUE) - dv_c[(decision_order * NUM_INPUTS_RBF * NUM_RBF) + NUM_INPUTS_RBF * i + 3]) ** 2) \
                    / (dv_b[(decision_order * NUM_INPUTS_RBF * NUM_RBF) + NUM_INPUTS_RBF * i + 3]) ** 2
      cash_out += dv_w[decision_order * NUM_RBF + i] * np.exp(arg_exp)
    elif (SHARED_RBFS == 1):
      arg_exp = -((f_fund_balance * useinrbf_fund_withdrawal / NORMALIZE_FUND - dv_c[NUM_INPUTS_RBF * i]) ** 2) \
                    / (dv_b[NUM_INPUTS_RBF * i]) ** 2\
                -((f_debt * useinrbf_debt_withdrawal / NORMALIZE_FUND - dv_c[NUM_INPUTS_RBF * i + 1]) ** 2) \
                    / (dv_b[NUM_INPUTS_RBF * i + 1]) ** 2\
                -((f_power_price_index * useinrbf_power_withdrawal / NORMALIZE_POWER_PRICE - dv_c[NUM_INPUTS_RBF * i + 2]) ** 2) \
                    / (dv_b[NUM_INPUTS_RBF * i + 2]) ** 2\
                -(((f_cash_in * useinrbf_cashin_withdrawal + NORMALIZE_REVENUE) / (2 * NORMALIZE_REVENUE) - dv_c[NUM_INPUTS_RBF * i + 3]) ** 2) \
                    / (dv_b[NUM_INPUTS_RBF * i + 3]) ** 2
      cash_out += dv_w[decision_order * NUM_RBF + i] * np.exp(arg_exp)
    else:
      cash_out += 0
  # add constant term
  cash_out += dv_a[decision_order]
  # now scale back to [-NORMALIZE_REVENUE,NORMALIZE_REVENUE]
  cash_out = max(min((cash_out * 2 * NORMALIZE_REVENUE) - NORMALIZE_REVENUE, NORMALIZE_REVENUE), -NORMALIZE_REVENUE)
  # now write as withdrawal for policy return
  withdrawal = cash_out - f_cash_in
  # ensure that cant withdraw more than fund balance
  if (withdrawal > EPS):
    withdrawal = min(withdrawal, f_fund_balance)
  elif (withdrawal < -EPS):
    withdrawal = max(withdrawal, -max(f_cash_in, 0))
  if ((f_fund_balance - withdrawal) > dv_d[decision_order] * NORMALIZE_FUND):
    withdrawal = (f_fund_balance - (dv_d[decision_order] * NORMALIZE_FUND))
  return withdrawal


### get hedging contract slope each year from static 2-dv policy based on current conditions
def policy_cashflow_post_withdrawal_2dv(fund_balance, cash_in, cashflow_target, maxFund):
  if (cash_in < cashflow_target):
    if (fund_balance < EPS):
      x = cash_in
    else:
      x = min(cash_in + fund_balance, cashflow_target)
  else:
    if (fund_balance > (maxFund - EPS)):
      x = cash_in + (fund_balance - maxFund)
    else:
      x = max(cash_in - (maxFund - fund_balance), cashflow_target)
  return(x)







### plot static & dynamic policy trajectories over wet & dry periods
def plot_example_simulation(ref_2dv_2obj_retest, ref_dps_2obj_retest, fig_format):

  example_data = pd.read_csv(dir_generated_inputs + '/example_data.csv', sep=' ', index_col=0)
  ny = example_data.shape[0] - 1

  ind_2dv = np.where(ref_2dv_2obj_retest.relCloseness_2obj == ref_2dv_2obj_retest.relCloseness_2obj.max())[0][0]
  ind_dps = np.where(ref_dps_2obj_retest.relCloseness_2obj == ref_dps_2obj_retest.relCloseness_2obj.max())[0][0]

  soln_2dv = ref_2dv_2obj_retest.iloc[ind_2dv, :]
  soln_dps = ref_dps_2obj_retest.iloc[ind_dps, :]

  policies = [soln_2dv, soln_dps]
  dps_run_types = [0, 1]
  cols = [col_reds[2], col_blues[2], 'k']

  lss = ['-','-.']
  realization = ['_wet', '_dry']


  fig = plt.figure(figsize=(6,10))
  gs1 = fig.add_gridspec(nrows=4, ncols=3, left=0, right=1, wspace=0.1, hspace=0.1)

  ax = fig.add_subplot(gs1[0,0])
  ax.annotate('a)', xy=(0.01, 0.89), xycoords='axes fraction')
  ax.set_ylabel('SWE Index\n(inch)')
  ax.set_yticks([0,30,60])
  ax.tick_params(axis='y',which='both',labelleft=True,labelright=False)
  ax.tick_params(axis='x',which='both',labelbottom=False,labeltop=False)
  ax.xaxis.set_label_position('top')
  ax.axhline(0, color='0.5', ls=':', zorder=1)
  ax.plot(range(1, ny+1), example_data['sweIndex_wet'][1:], c=cols[2], ls=lss[0], lw=1.5)
  ax.plot(range(1, ny+1), example_data['sweIndex_dry'][1:], c=cols[2], ls=lss[1], lw=1.5)

  ax0 = fig.add_subplot(gs1[1,0], sharex=ax)
  ax0.annotate('b)', xy=(0.01, 0.89), xycoords='axes fraction')
  ax0.set_ylabel('Generation\n(TWh)')
  ax0.set_yticks([1, 1.5, 2, 2.5])
  ax0.tick_params(axis='y',which='both',labelleft=True,labelright=False)
  ax0.tick_params(axis='x',which='both',labelbottom=False,labeltop=False)
  ax0.plot(range(1, ny+1), example_data['gen_wet'][1:], c=cols[2], ls=lss[0], lw=1.5)
  ax0.plot(range(1, ny+1), example_data['gen_dry'][1:], c=cols[2], ls=lss[1], lw=1.5)

  ax0 = fig.add_subplot(gs1[2,0], sharex=ax)
  ax0.annotate('c)', xy=(0.01, 0.89), xycoords='axes fraction')
  ax0.set_ylabel('Wholesale Price\n(\$/MWh)')
  ax0.set_yticks([30, 45, 60])
  ax0.tick_params(axis='y',which='both',labelleft=True,labelright=False)
  ax0.tick_params(axis='x',which='both',labelbottom=False,labeltop=False)
  ax0.plot(range(ny+1), example_data['powWt_wet'], c=cols[2], ls=lss[0], lw=1.5)
  ax0.plot(range(ny+1), example_data['powWt_dry'], c=cols[2], ls=lss[1], lw=1.5)

  ax0 = fig.add_subplot(gs1[3,0], sharex=ax)
  ax0.annotate('d)', xy=(0.01, 0.89), xycoords='axes fraction')
  ax0.set_ylabel('Net Revenue\n(\$)')
  ax0.set_xlabel('Year')
  ax0.set_yticks([-20, 0, 20, 40])
  ax0.tick_params(axis='y',which='both',labelleft=True,labelright=False)
  ax0.tick_params(axis='x',which='both',labelbottom=True,labeltop=False)
  ax0.axhline(0, color='0.5', ls=':', zorder=1)
  ax0.plot(range(1, ny+1), example_data['rev_wet'][1:] - fixed_cost * MEAN_REVENUE, c=cols[2], ls=lss[0], lw=1.5)
  ax0.plot(range(1, ny+1), example_data['rev_dry'][1:] - fixed_cost * MEAN_REVENUE, c=cols[2], ls=lss[1], lw=1.5)

  ax01 = fig.add_subplot(gs1[0,1], sharex=ax)
  ax11 = fig.add_subplot(gs1[1,1], sharex=ax)
  ax21 = fig.add_subplot(gs1[2,1], sharex=ax)
  ax31 = fig.add_subplot(gs1[3,1], sharex=ax)
  ax02 = fig.add_subplot(gs1[0,2], sharex=ax, sharey=ax01)
  ax12 = fig.add_subplot(gs1[1,2], sharex=ax, sharey=ax11)
  ax22 = fig.add_subplot(gs1[2,2], sharex=ax, sharey=ax21)
  ax32 = fig.add_subplot(gs1[3,2], sharex=ax, sharey=ax31)
  axes = [[ax01, ax11, ax21, ax31], [ax02, ax12, ax22, ax32]]

  ### loop over policies
  for j in range(2):
    policy = policies[j]
    dps_run_type = dps_run_types[j]
    if dps_run_type == 1:
      dv_d, dv_c, dv_b, dv_w, dv_a = get_dvs(policy)

    ### loop over realizations
    for i in range(2):
      fund_hedge, fund_withdrawal, debt_hedge, debt_withdrawal, power_hedge, power_withdrawal, cash_in, action_hedge, action_withdrawal, final_cashflow = \
        simulate(example_data['rev' + realization[i]].values, example_data['cfd' + realization[i]].values, example_data['powIndex' + realization[i]].values, policy, dps_run_type)
      fund = np.append(fund_hedge, fund_withdrawal[-1])
      debt = np.append(debt_hedge, debt_withdrawal[-1])

      if (j==0):
        axes[i][0].tick_params(axis='x',which='both',labelbottom=False,labeltop=False)
        axes[i][0].yaxis.set_ticks_position('right')
        axes[i][0].axhline(0, color='0.5', ls=':', zorder=1)
        if (i==0):
          axes[i][0].annotate('e)', xy=(0.01, 0.89), xycoords='axes fraction')
          axes[i][0].tick_params(axis='y',which='both',labelleft=False,labelright=False)
        else:
          axes[i][0].annotate('i)', xy=(0.01, 0.89), xycoords='axes fraction')
          axes[i][0].set_ylabel('CFD Slope\n(\$M/inch)', rotation=270, labelpad=35)
          axes[i][0].yaxis.set_label_position('right')
          axes[i][0].tick_params(axis='y',which='both',labelleft=False,labelright=True)
          axes[i][0].set_yticks([0,0.4,0.8])
      axes[i][0].plot(range(ny), action_hedge, c=cols[j], ls=lss[i], lw=1.5)

      if (j==0):
        axes[i][1].axhline(0, color='0.5', ls=':', zorder=1)
        axes[i][1].tick_params(axis='x',which='both',labelbottom=False,labeltop=False)
        axes[i][1].yaxis.set_ticks_position('right')
        if (i==0):
          axes[i][1].annotate('f)', xy=(0.01, 0.89), xycoords='axes fraction')
          axes[i][1].tick_params(axis='y',which='both',labelleft=False,labelright=False)
        else:
          axes[i][1].annotate('j)', xy=(0.01, 0.89), xycoords='axes fraction')
          axes[i][1].set_ylabel('Fund Balance\n(\$M)', rotation=270, labelpad=35)
          axes[i][1].yaxis.set_label_position('right')
          axes[i][1].tick_params(axis='y',which='both',labelleft=False,labelright=True)
          axes[i][1].set_yticks([0,10,20])
      axes[i][1].plot(range(ny+1), fund, c=cols[j], ls=lss[i], lw=1.5)

      if (j==0):
        axes[i][2].axhline(0, color='0.5', ls=':', zorder=1)
        axes[i][2].tick_params(axis='x',which='both',labelbottom=False,labeltop=False)
        axes[i][2].yaxis.set_ticks_position('right')
        if (i==0):
          axes[i][2].annotate('g)', xy=(0.01, 0.89), xycoords='axes fraction')
          axes[i][2].tick_params(axis='y',which='both',labelleft=False,labelright=False)
        else:
          axes[i][2].annotate('k)', xy=(0.01, 0.89), xycoords='axes fraction')
          axes[i][2].set_ylabel('Debt\n(\$M)', rotation=270, labelpad=35)
          axes[i][2].yaxis.set_label_position('right')
          axes[i][2].tick_params(axis='y',which='both',labelleft=False,labelright=True)
          axes[i][2].set_yticks([0,5,10,15])
      axes[i][2].plot(range(ny+1), debt, c=cols[j], ls=lss[i], lw=1.5)

      if (j==0):
        axes[i][3].axhline(0, color='0.5', ls=':', zorder=1)
        axes[i][3].set_xlabel('Year') 
        axes[i][3].yaxis.set_ticks_position('right')
        if (i==0):
          axes[i][3].annotate('h)', xy=(0.01, 0.89), xycoords='axes fraction')
          axes[i][3].tick_params(axis='y',which='both',labelleft=False,labelright=False)
        else:
          axes[i][3].annotate('l)', xy=(0.01, 0.89), xycoords='axes fraction')
          axes[i][3].set_ylabel('Final Cashflow\n(\$M)', rotation=270, labelpad=35)
          axes[i][3].yaxis.set_label_position('right')
          axes[i][3].tick_params(axis='y',which='both',labelleft=False,labelright=True)
          axes[i][3].set_yticks([0,20,40])
      axes[i][3].plot(range(1, ny+1), final_cashflow, c=cols[j], ls=lss[i], lw=1.5)

  legend_elements = [Line2D([0], [0], color=cols[2], lw=1.5, label='Stochastic driver'),
                      Line2D([0], [0], color=cols[0], lw=1.5, label='Static policy'),
                      Line2D([0], [0], color=cols[1], lw=1.5, label='Dynamic policy'),
                      Line2D([0], [0], color='grey', lw=1.5, label='Wet realization'),
                      Line2D([0], [0], color='grey', lw=1.5, ls='-.', label='Dry realization'),]

  axes[i][3].legend(handles=legend_elements, ncol=2, bbox_to_anchor=(2,-0.35))#, fontsize=12)

  plt.savefig(dir_figs + 'exampleSim_dynStat.' + fig_format, bbox_inches='tight', dpi=500)

  return
