import seaborn as sns; sns.set(style="ticks", color_codes=True)
from matplotlib import pyplot as plt

iris = sns.load_dataset("iris")
g = sns.pairplot(iris, diag_kind = 'kde')

pp_rows = len(g.axes)
pp_cols = len(g.axes[0])

fig, axs = plt.subplots(pp_rows, pp_cols, figsize=(12,12))

xlabels, ylabels = [], []

for ax in g.axes[-1,:]:
    xlabel = ax.xaxis.get_label_text()
    xlabels.append(xlabel)
for ax in g.axes[:,0]:
    ylabel = ax.yaxis.get_label_text()
    ylabels.append(ylabel)

for i in range(len(xlabels)):
    for j in range(len(ylabels)):
        if i != j:
            # Diagnol
            sns.regplot(x=xlabels[i], y=ylabels[j], data=iris, scatter=True, fit_reg=False, ax=axs[j ,i])
        else:
            sns.kdeplot(iris[xlabels[i]], ax=axs[j ,i])

        # Fix plot labels
        if i == 0:
            axs[j ,i].set_xlabel("")
            axs[j ,i].set_ylabel(ylabels[j])
        elif j == len(xlabels)-1:
            axs[j ,i].set_xlabel(xlabels[i])
            axs[j ,i].set_ylabel("")
        else:
            axs[j ,i].set_xlabel("")
            axs[j ,i].set_ylabel("")




