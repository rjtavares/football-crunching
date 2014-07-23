import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

x_size = 105.0
y_size = 68.0

type_names = {1: 'PASS', 2:'OFFSIDE PASS', 3: 'DRIBBLE', 4:'FOUL (1-ON, 0-BY)', 5: 'PLAY_ACTORS',
              6:'CORNER (1-WON, 0-GRANTED)', 7: 'TACKLE', 8:'INTERCEPTION',
              10: 'SAVE/BLOCK', 11: 'GK GRAB BALL', 12: 'INTERCEPTION (NO CONTROL)',
              13: 'SHOT OFF GOAL', 14: 'SHOT HIT POST', 15: 'SHOT ON GOAL', 16: 'GOAL',
              17: 'YELLOW CARD', 18: 'SUBSTITUTION (OFF)', 19: 'SUBSTITUTION (ON)', 34:'????????',
              41: 'GK PUNCH', 42: 'something awesome', 43: '???????????', 44:'HEADING DUEL',
              45: 'TACKLE (MISSED)', 49: 'WON CONTROL OF BALL', 50:'LOST CONTROL OF BALL', 51:'INTERCEPTION (MISSED)', 
              52: 'gk action', 55:'offside defender', 56:'??????????', 59: 'gk action',
              61: 'LOST CONTROL OF BALL', 74: 'CLEAR BALL (OUT OF PITCH)', 100: 'RECEPTION', 101: 'RUN WITH BALL', 102: 'LINEUP'}

def draw_events(events, alpha=1, base_color='black', goal_color='red', mirror_away=False, arrows=True):       
    for i, event in events.iterrows():
        side = event['side']
        if mirror_away:
            mirror = side=='A'
        else:
            mirror = False
        if mirror:
            x = x_size-event['x']
            y = y_size-event['y']
            dx = -(event['to_x']-event['x'])
            dy = -(event['to_y']-event['y'])
        else:
            x = event['x']
            y = event['y']
            dx = event['to_x']-event['x']
            dy = event['to_y']-event['y']

        if event['type']==16:
            color = goal_color
        else:
            color = base_color
        
        if pd.notnull(event['to_x']):
            if event['type']==101:
                style='dotted'
                head_width=1*arrows
                head_length=1*arrows
            else:
                style='solid'
                head_width=2*arrows
                head_length=2*arrows
                
            plt.arrow(x, y, dx, dy, head_width=head_width, head_length=head_length, linestyle=style,
                      color=color, alpha=alpha, length_includes_head=True)
        else:
            plt.scatter(x,y, marker='x', color=color, alpha=alpha)

def draw_pitch():
    #set up field    
    fig = plt.figure(figsize=(x_size/10, y_size/10))
    fig.patch.set_facecolor('#78AB46')

    axes = fig.add_subplot(1, 1, 1, axisbg='#78AB46')

    axes.xaxis.set_visible(False)
    axes.yaxis.set_visible(False)

    plt.xlim([-5,x_size+5])
    plt.ylim([-5,y_size+5])

    box_height = ((16.5*2 + 7.32)/y_size)/1.15
    box_width = (16.5/x_size)/1.15

    team_colors = {'H': 'red',
                   'A': 'white'}    

    r1 = plt.Rectangle((0.04338, 0.0641), (0.95652-0.04338), (0.9359-0.0641),
                       edgecolor="white", facecolor="none", alpha=1, transform=axes.transAxes) #pitch

    r2 = plt.Line2D([0.5, 0.5], [0.9359, 0.0641],
                    c='w', transform=axes.transAxes) #half-way line

    r3 = plt.Rectangle((0.04338, (1-box_height)/2), box_width, box_height,
                       ec='w', fc='none', transform=axes.transAxes) #penalty area

    r4 = plt.Rectangle((0.95652-box_width, (1-box_height)/2), box_width, box_height,
                       ec='w', fc='none', transform=axes.transAxes) #penalty area

    r5 = Ellipse((0.5, 0.5), 9.15*2/x_size, 9.15*2/y_size,
                                    ec='w', fc='none', transform=axes.transAxes) #middle circle

    fig.lines.extend([r1, r2, r3, r4, r5])
    
    return fig, axes