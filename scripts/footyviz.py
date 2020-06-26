from matplotlib import pyplot as plt
from matplotlib.patches import Ellipse
from matplotlib.collections import PatchCollection
import matplotlib.patheffects as path_effects
import numpy as np

from scipy.spatial import Voronoi
from shapely.geometry import Polygon

X_SIZE = 105
Y_SIZE = 68

BOX_HEIGHT = (16.5*2 + 7.32)/Y_SIZE*100
BOX_WIDTH = 16.5/X_SIZE*100

GOAL = 7.32/Y_SIZE*100

GOAL_AREA_HEIGHT = 5.4864*2/Y_SIZE*100 + GOAL
GOAL_AREA_WIDTH = 5.4864/X_SIZE*100

SCALERS = np.array([X_SIZE/100, Y_SIZE/100])
pitch_polygon = Polygon(((0,0), (0,100), (100,100), (100,0)))

def draw_pitch(dpi=100, pitch_color='#a8bc95', fig=None, ax=None, size=1):
    """Sets up field
    Returns matplotlib fig and axes objects.
    """
    if fig is None:
        figsize=(12.8*size, 7.2*size)
        fig = plt.figure(figsize=figsize, dpi=dpi)
    fig.patch.set_facecolor(pitch_color)

    if ax is None:
        ax = fig.add_subplot(1, 1, 1)
    ax.set_axis_off()
    ax.set_facecolor(pitch_color)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)

    ax.set_xlim(0,100)
    ax.set_ylim(0,100)

    plt.xlim([-13.32, 113.32])
    plt.ylim([-5, 105])

    fig.tight_layout(pad=3)

    draw_patches(ax)

    return fig, ax

def draw_patches(axes):
    """
    Draws basic field shapes on an axes
    """
    #pitch
    axes.add_patch(plt.Rectangle((0, 0), 100, 100,
                       edgecolor="white", facecolor="none"))

    #half-way line
    axes.add_line(plt.Line2D([50, 50], [100, 0],
                    c='w'))

    #penalty areas
    axes.add_patch(plt.Rectangle((100-BOX_WIDTH, (100-BOX_HEIGHT)/2),  BOX_WIDTH, BOX_HEIGHT,
                       ec='w', fc='none'))
    axes.add_patch(plt.Rectangle((0, (100-BOX_HEIGHT)/2),  BOX_WIDTH, BOX_HEIGHT,
                               ec='w', fc='none'))

    #goal areas
    axes.add_patch(plt.Rectangle((100-GOAL_AREA_WIDTH, (100-GOAL_AREA_HEIGHT)/2),  GOAL_AREA_WIDTH, GOAL_AREA_HEIGHT,
                       ec='w', fc='none'))
    axes.add_patch(plt.Rectangle((0, (100-GOAL_AREA_HEIGHT)/2),  GOAL_AREA_WIDTH, GOAL_AREA_HEIGHT,
                               ec='w', fc='none'))

    #goals
    axes.add_patch(plt.Rectangle((100, (100-GOAL)/2),  1, GOAL,
                       ec='w', fc='none'))
    axes.add_patch(plt.Rectangle((0, (100-GOAL)/2),  -1, GOAL,
                               ec='w', fc='none'))


    #halfway circle
    axes.add_patch(Ellipse((50, 50), 2*9.15/X_SIZE*100, 2*9.15/Y_SIZE*100,
                                    ec='w', fc='none'))

    return axes

def draw_frame(df, t, fig=None, ax=None, size=1, dpi=100, fps=20, label='player_num', show_players=True,
               highlight_color=None, highlight_player=None, text_size=8, text_color='white', flip=False, voronoi=False, **anim_args):
    """
    Draws players from time t (in seconds) from a DataFrame df
    """
    fig, ax = draw_pitch(dpi=dpi, fig=fig, ax=ax, size=size)

    dfFrame = get_frame(df, t, fps=fps)
 
    if show_players:
        fig, ax, dfFrame = add_players(fig, ax, dfFrame,
                                       label=label, highlight_color=highlight_color, highlight_player= highlight_player, 
                                       text_size=text_size, text_color=text_color)
    if voronoi == True:
        fig, ax, dfFrame = add_voronoi(fig, ax, dfFrame)
    return fig, ax, dfFrame

def add_players(fig, ax, dfFrame, label='player_num', highlight_color=None, highlight_player=None, text_size=8, text_color='white'):
    for pid in dfFrame.index:
        if pid==0:
            #se for bola
            try:
                z = dfFrame.loc[pid]['z']
            except:
                z = 0
            size = 1.2+z
            lw = 0.9
            color='black'
            edge='white'
            zorder = 100
        else:
            #se for jogador
            size = 3
            lw = 2
            edge = dfFrame.loc[pid]['edgecolor']

            if pid == highlight_player:
                color = highlight_color
            else:
                color = dfFrame.loc[pid]['bgcolor']
            if dfFrame.loc[pid]['team']=='attack':
                zorder = 21
            else:
                zorder = 20

        ax.add_artist(Ellipse((dfFrame.loc[pid]['x'],
                            dfFrame.loc[pid]['y']),
                            size/X_SIZE*100, size/Y_SIZE*100,
                            edgecolor=edge,
                            linewidth=lw,
                            facecolor=color,
                            alpha=0.8,
                            zorder=zorder))

        if text_color is not None:
            try:
                s = dfFrame.loc[pid][label]
                if isinstance(s, str)==False:
                    s = str(int(label))
            except:
                s = ''
            text = plt.text(dfFrame.loc[pid]['x'],dfFrame.loc[pid]['y'],s,
                            horizontalalignment='center', verticalalignment='center',
                            fontsize=text_size, color=text_color, zorder=22, alpha=0.8)

            text.set_path_effects([path_effects.Stroke(linewidth=1, foreground=text_color, alpha=0.8),
                                path_effects.Normal()])

    return fig, ax, dfFrame
    
    
def add_voronoi(fig, ax, dfFrame):
    polygons = {}
    vor, dfVor = calculate_voronoi(dfFrame)
    for index, region in enumerate(vor.regions):
        if not -1 in region:
            if len(region)>0:
                try:
                    pl = dfVor[dfVor['region']==index]
                    polygon = Polygon([vor.vertices[i] for i in region]/SCALERS).intersection(pitch_polygon)
                    polygons[pl.index[0]] = polygon
                    color = pl['bgcolor'].values[0]
                    x, y = polygon.exterior.xy
                    plt.fill(x, y, c=color, alpha=0.30)
                except IndexError:
                    pass
                except AttributeError:
                    pass

    plt.scatter(dfVor['x'], dfVor['y'], c=dfVor['bgcolor'], alpha=0.2)

    return fig, ax, dfFrame

def calculate_voronoi(dfFrame):
    dfTemp = dfFrame.copy().drop(0, errors='ignore')

    values = np.vstack((dfTemp[['x', 'y']].values*SCALERS,
                        [-1000,-1000],
                        [+1000,+1000],
                        [+1000,-1000],
                        [-1000,+1000]
                       ))

    vor = Voronoi(values)

    dfTemp['region'] = vor.point_region[:-4]

    return vor, dfTemp

def get_frame(df, t, fps=20):
    dfFrame = df.loc[int(t*fps)].set_index('player')
    return dfFrame