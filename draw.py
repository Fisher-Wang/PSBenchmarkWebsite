# Author: Jijie Ren
# Modified by: Feishi Wang
# ref: https://jdhao.github.io/2017/06/11/mpl_multiplot_one_colorbar/

import seaborn as sns
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.pyplot as plt
import numpy as np
from config import show

def plot(df_mean, shapes, textures):

    matrix = df_mean.to_numpy().astype('float64')

    fig, ax = plt.subplots(1, 1, figsize=(5,5))

    s0=10;s1=12;s2=15;s3=15;ss=20;
    m1cmap = sns.color_palette('coolwarm', as_cmap=True,n_colors=40)

    divider = make_axes_locatable(ax)
    cax = divider.new_horizontal(size="5%", pad=0.1, pack_start=False)
    fig.add_axes(cax)


    g = sns.heatmap(matrix, vmin=0, vmax=45, ax=ax, annot=True, 
                    annot_kws={"size": s2}, 
                    square=False, 
                    cmap=m1cmap,
                    cbar=1,
                    cbar_ax=cax,cbar_kws={"label": 'Mean Angular Error (degree)'}) 



    plt.tick_params(axis='x', labelbottom=False)
    plt.tick_params(axis='y', labelleft=False)

    cax.tick_params(labelsize=s3)
    cax.yaxis.label.set_size(fontsize=ss)

    plt.tick_params(axis='x', labelbottom=True);
    g.set_xticklabels(textures, fontsize=s3, rotation=70)

    ax.tick_params(axis='y', labelleft=True)
    g.set_yticklabels(shapes, fontsize=s3, rotation=0)

    plt.title('(%.2f/%.2f)' % (np.mean(matrix) , np.median(matrix)), fontsize=ss, fontweight='bold', y=1.05)

    # plt.show()
    return fig