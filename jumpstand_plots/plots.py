import pandas as pnd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def preproc_jumpstand(input_file, plot_type):
    """
    Read and preprocess data to further use

    :param input_file : path like object or string
    :param plot_type  : string ('stacked_bars', 'pie_charts' or 'progress')
    :return : pandas.dataframe or None
            if plot_type == 'stacked_bars':
                main data with additional columns
            if plot_type == 'pie_charts' or 'progress':
                numbers of cases
            else:
                None
    """

    # Read CSV file
    df = pd.read_csv(input_file)

    # Get final outcome
    outcome = []
    for i in df.index:
        outcome.append('P' if df['lickOutcome'].loc[i] == 1 and df['jumpOutcome'].loc[i] == 1 else
                       'J' if df['lickOutcome'].loc[i] == 0 and df['jumpOutcome'].loc[i] == 1 else
                       'L' if df['lickOutcome'].loc[i] == 1 and df['jumpOutcome'].loc[i] == 0 else
                       'F')
    df['finalOutcome'] = outcome

    # Stacked bars
    if plot_type == 'stacked_bars':
        # calculate lick-next trial time
        lick_next = []
        for i in df.iloc[:-1].index:
            lick_next.append(df['trialInitTime'].loc[i + 1] - df['trialInitTime'].loc[i]
                             - df['jumpTime'].loc[i] - df['lickTime'].loc[i])
        lick_next.append(0)
        df['lickNext'] = lick_next

        # calculate trial length
        trial_length = df['jumpTime'] + df['lickTime'] + df['lickNext']
        df['trialLength'] = trial_length

        return df

    # Pie charts or Progress
    if plot_type == 'pie_charts' or plot_type == 'progress':
        rateData = {
            "nTrialsPassed": [0, 0, 0],
            "nCorrectJumps": [0, 0, 0],
            "nCorrectLicks": [0, 0, 0],
            "nTrialsFailed": [0, 0, 0]
        }
        rateDF = pd.DataFrame(rateData, index=['all', 'left', 'right'])

        # all
        rateDF['nTrialsPassed'].loc['all'] = df[df['finalOutcome'] == 'P']['trialInitTime'].count()
        rateDF['nCorrectJumps'].loc['all'] = df[df['finalOutcome'] == 'J']['trialInitTime'].count()
        rateDF['nCorrectLicks'].loc['all'] = df[df['finalOutcome'] == 'L']['trialInitTime'].count()
        rateDF['nTrialsFailed'].loc['all'] = df[df['finalOutcome'] == 'F']['trialInitTime'].count()

        # left
        rateDF['nTrialsPassed'].loc['left'] = df[(df['finalOutcome'] == 'P') &
                                                 (df['verticalSide'] == 'left')]['trialInitTime'].count()
        rateDF['nCorrectJumps'].loc['left'] = df[(df['finalOutcome'] == 'J') &
                                                 (df['verticalSide'] == 'left')]['trialInitTime'].count()
        rateDF['nCorrectLicks'].loc['left'] = df[(df['finalOutcome'] == 'L') &
                                                 (df['verticalSide'] == 'left')]['trialInitTime'].count()
        rateDF['nTrialsFailed'].loc['left'] = df[(df['finalOutcome'] == 'F') &
                                                 (df['verticalSide'] == 'left')]['trialInitTime'].count()

        # right
        rateDF['nTrialsPassed'].loc['right'] = df[(df['finalOutcome'] == 'P') &
                                                  (df['verticalSide'] == 'right')]['trialInitTime'].count()
        rateDF['nCorrectJumps'].loc['right'] = df[(df['finalOutcome'] == 'J') &
                                                  (df['verticalSide'] == 'right')]['trialInitTime'].count()
        rateDF['nCorrectLicks'].loc['right'] = df[(df['finalOutcome'] == 'L') &
                                                  (df['verticalSide'] == 'right')]['trialInitTime'].count()
        rateDF['nTrialsFailed'].loc['right'] = df[(df['finalOutcome'] == 'F') &
                                                  (df['verticalSide'] == 'right')]['trialInitTime'].count()

        return rateDF

    # Wrong plot type
    else:
        return None


def stacked_bar_jumpstand(subject: str, date: str, file, ver_vs_hor=False):
    """
    Plot stacked bar plot with advanced color coding

    :param subject    : subject's name
    :param date       : date of the experiment
    :param file       : input file path
    :param ver_vs_hor : vertical vs horizontal or vertical vs grey
    :return:
    """
    # Prepare data & figure
    df = preproc_jumpstand(input_file=file, plot_type='stacked_bars')
    times = [df['jumpTime'], df['lickTime'], df['lickNext']]
    width = 0.45

    fig, ax = plt.subplots(figsize=(max(df['jumpTime'].size / 2, 10), 10))

    # ## color-hatch-label patches --> legend
    jump_l_cor = mpatches.Patch(edgecolor='k', facecolor='blue', hatch='', label='left trial, correct jump')
    jump_l_wro = mpatches.Patch(facecolor='cornflowerblue', hatch='///', label='left trial, wrong jump')

    jump_r_cor = mpatches.Patch(facecolor='darkorange', hatch='', label='right trial, correct jump')
    jump_r_wro = mpatches.Patch(facecolor='moccasin', hatch='\\\\\\', label='right trial, wrong jump')

    lick_in_time = mpatches.Patch(facecolor='lawngreen', hatch='', label='lick in time')
    lick_timeout = mpatches.Patch(facecolor='fuchsia', hatch='', label='lick timeout')
    lick_wrong = mpatches.Patch(facecolor='brown', hatch='', label='lick wrong time')

    inter_t_t = mpatches.Patch(facecolor='silver', label='lick to next')

    legend = [jump_l_cor, jump_l_wro, jump_r_cor, jump_r_wro, lick_in_time, lick_timeout, lick_wrong, inter_t_t]

    # ## coloring each bar segments (jump, lick, lick-to-next)
    colors = [[], [], []]
    hatches = [[], [], []]
    for i in df.index:
        if df['verticalSide'].loc[i] == 'left':
            if df['finalOutcome'].loc[i] == 'P' or df['finalOutcome'].loc[i] == 'J':
                colors[0].append(jump_l_cor.get_facecolor())
                hatches[0].append(jump_l_cor.get_hatch())
            else:
                colors[0].append(jump_l_wro.get_facecolor())
                hatches[0].append(jump_l_wro.get_hatch())
        elif df['verticalSide'].loc[i] == 'right':
            if df['finalOutcome'].loc[i] == 'P' or df['finalOutcome'].loc[i] == 'J':
                colors[0].append(jump_r_cor.get_facecolor())
                hatches[0].append(jump_r_cor.get_hatch())
            else:
                colors[0].append(jump_r_wro.get_facecolor())
                hatches[0].append(jump_r_wro.get_hatch())

        if df['finalOutcome'].loc[i] == 'P':
            colors[1].append(lick_in_time.get_facecolor())
        elif df['finalOutcome'].loc[i] == 'J':
            colors[1].append(lick_timeout.get_facecolor())
        elif df['finalOutcome'].loc[i] == 'F' or df['finalOutcome'].loc[i] == 'L':
            colors[1].append(lick_wrong.get_facecolor())
        hatches[1].append('')

        colors[2].append(inter_t_t.get_facecolor())
        hatches[2].append('')

    label = ["start to jump", "jump to lick", "lick to next"]
    p = []
    bottom = np.zeros(df['jumpTime'].size)

    ######################################
    # Stocked bar plot (advanced coloring)
    ######################################
    for i in range(len(colors)):
        p.append(
            ax.bar(list(df.index.values) + np.ones(df['jumpTime'].size), times[i], width, label=label[i], bottom=bottom,
                   color=colors[i], hatch=hatches[i], edgecolor='k'))
        bottom += times[i]

    # Lagand & labels
    bar_labels = [f"{s[0]}::{out[0]}" for s, out in zip(df['verticalSide'], df['finalOutcome'])]
    for i, v in enumerate(bar_labels):
        ax.text(i + 1, 0, v, ha='center')

    ax.set_title(f"{'Vertical vs Horizontal' if ver_vs_hor else 'Vertical vs Grey'} JumpStand training\n"
                 f"{subject}, {date}")
    ax.set_xlabel("trials")
    ax.set_ylabel("time elapsed from trial initiation [s]")

    # ## limit the plotted trial time in 60 if some of them is greater
    if df['trialLength'].max() > 60:
        plt.ylim(0, 60)

    ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1.15), ncol=1, handles=legend)

    plt.grid()


def double_pie_chart_jumpstand(subject: str, date: str, file, ver_vs_hor=False):
    """
    Plot double pie charts with advanced color coding

    :param subject    : subject's name
    :param date       : date of the experiment
    :param file       : input file path
    :param ver_vs_hor : vertical vs horizontal or vertical vs grey
    :return:
    """
    # Prepare data & figure
    df = preproc_jumpstand(input_file=file, plot_type='pie_charts')
    print(df)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle(f"{'Vertical vs Horizontal' if ver_vs_hor else 'Vertical vs Grey'} JumpStand training\n"
                 f"{subject}, {date}")

    inner_labels = ['jumped correctly', 'jumped wrongly']
    outer_labels = ['lick', 'no lick']

    inner_colors = ['green', 'red', 'red', 'green']
    outer_colors = ['orange', 'grey', 'grey', 'orange', 'orange', 'grey', 'grey', 'orange']

    outer_hatches = ['', '', '', '////', '////', '', '', '']

    ###############################
    # Pie chart grouped by trial
    ###############################
    inner_data = [df['nTrialsPassed'].loc['left'] + df['nCorrectJumps'].loc['left'],
                  df['nCorrectLicks'].loc['left'] + df['nTrialsFailed'].loc['left'],
                  df['nCorrectLicks'].loc['right'] + df['nTrialsFailed'].loc['right'],
                  df['nTrialsPassed'].loc['right'] + df['nCorrectJumps'].loc['right']]
    outer_data = list(df.loc['left']) + list(df.loc['right'])[::-1]

    size = 0.2

    ax1.set_aspect('equal')

    # Outer pie chart
    o_wedges, texts, percs = ax1.pie(outer_data, radius=1, colors=outer_colors,
                                     wedgeprops=dict(width=size, edgecolor='k'),
                                     autopct="%1.1f%%", startangle=90, pctdistance=1.2,
                                     hatch=outer_hatches)

    groups = [[0, 1, 2, 3], [4, 5, 6, 7]]
    outer_radfraction = 0.05
    for group in groups:
        ang = np.deg2rad((o_wedges[group[-1]].theta2 + o_wedges[group[0]].theta1) / 2)
        for j in group:
            center = outer_radfraction * o_wedges[j].r * np.array([np.cos(ang), np.sin(ang)])
            o_wedges[j].set_center(center)
            texts[j].set_position(np.array(texts[j].get_position()) + center)
            percs[j].set_position(np.array(percs[j].get_position()) + center)
    ax1.autoscale(True)

    # Inner pie chart
    i_wedges, texts, percs = ax1.pie(inner_data, radius=1 - size, colors=inner_colors,
                                     wedgeprops=dict(width=1 - size, edgecolor='k'),
                                     autopct="%1.1f%%", startangle=90)

    groups = [[0, 1], [2, 3]]
    inner_radfraction = outer_radfraction / (1 - size)
    for group in groups:
        ang = np.deg2rad((i_wedges[group[-1]].theta2 + i_wedges[group[0]].theta1) / 2)
        for j in group:
            center = inner_radfraction * i_wedges[j].r * np.array([np.cos(ang), np.sin(ang)])
            i_wedges[j].set_center(center)
            texts[j].set_position(np.array(texts[j].get_position()) + center)
            percs[j].set_position(np.array(percs[j].get_position()) + center)
    ax1.autoscale(True)

    # Legend & labels
    ax1.legend([i_wedges[0], i_wedges[1], o_wedges[0], o_wedges[1], o_wedges[3]],
               inner_labels + outer_labels + ["wrong lick"],
               loc=(-0.4, 0.01))

    ax1.text(-1.2, 1, f"left trials\n({df.loc['left'].sum()})", fontsize="large", fontweight="bold", ha="center")
    ax1.text(0.8, 1, f"right trials\n({df.loc['right'].sum()})", fontsize="large", fontweight="bold", ha="center")
    ax1.text(-2, 0.7, "Trial outcomes grouped\nby left & right trials", ha='left',
             bbox=dict(boxstyle="round", fc="w", ec="grey"))

    ###############################
    # Pie chart grouped by jumps
    ###############################
    inner_data = [df['nTrialsPassed'].loc['left'] + df['nCorrectJumps'].loc['left'],
                  df['nCorrectLicks'].loc['right'] + df['nTrialsFailed'].loc['right'],
                  df['nCorrectLicks'].loc['left'] + df['nTrialsFailed'].loc['left'],
                  df['nTrialsPassed'].loc['right'] + df['nCorrectJumps'].loc['right']]
    outer_data = list(df.loc['left'])[:2] + list(df.loc['right'])[2:] + \
                 list(df.loc['left'])[2:][::-1] + list(df.loc['right'][:2][::-1])
    print(inner_data)
    print(outer_data)

    size = 0.2
    ax1.set_aspect('equal')

    # Outer pie chart
    o_wedges, texts, percs = ax2.pie(outer_data, radius=1, colors=outer_colors,
                                     wedgeprops=dict(width=size, edgecolor='k'),
                                     autopct="%1.1f%%", startangle=90, pctdistance=1.2,
                                     hatch=outer_hatches)

    groups = [[0, 1, 2, 3], [4, 5, 6, 7]]
    outer_radfraction = 0.05
    for group in groups:
        ang = np.deg2rad((o_wedges[group[-1]].theta2 + o_wedges[group[0]].theta1) / 2)
        for j in group:
            center = outer_radfraction * o_wedges[j].r * np.array([np.cos(ang), np.sin(ang)])
            o_wedges[j].set_center(center)
            texts[j].set_position(np.array(texts[j].get_position()) + center)
            percs[j].set_position(np.array(percs[j].get_position()) + center)
    ax2.autoscale(True)

    # Inner pie chart
    i_wedges, texts, percs = ax2.pie(inner_data, radius=1 - size, colors=inner_colors,
                                     wedgeprops=dict(width=1 - size, edgecolor='k'),
                                     autopct="%1.1f%%", startangle=90)

    groups = [[0, 1], [2, 3]]
    inner_radfraction = outer_radfraction / (1 - size)
    for group in groups:
        ang = np.deg2rad((i_wedges[group[-1]].theta2 + i_wedges[group[0]].theta1) / 2)
        for j in group:
            center = inner_radfraction * i_wedges[j].r * np.array([np.cos(ang), np.sin(ang)])
            i_wedges[j].set_center(center)
            texts[j].set_position(np.array(texts[j].get_position()) + center)
            percs[j].set_position(np.array(percs[j].get_position()) + center)
    ax2.autoscale(True)

    # Legend & labels
    ax2.legend([i_wedges[0], i_wedges[1], o_wedges[0], o_wedges[1], o_wedges[3]],
               inner_labels + outer_labels + ["wrong lick"],
               loc=(0.9, 0.01))

    ax2.text(-1.2, 1, f"left jumps\n({sum(outer_data[:4])})", fontsize="large", fontweight="bold", ha="center")
    ax2.text(0.8, 1, f"right jumps\n({sum(outer_data[4:])})", fontsize="large", fontweight="bold", ha="center")
    ax2.text(1.2, 0.7, "Trial outcomes grouped\nby left & right jumps", ha='left',
             bbox=dict(boxstyle="round", fc="w", ec="grey"))


if __name__ == '__main__':
    double_pie_chart_jumpstand(subject='Tyapa', date='yyyy-mm-dd', file='data/jsVH2023-07-12_14h.40.03.csv')
    stacked_bar_jumpstand(subject='Tyapa', date='yyyy-mm-dd', file='data/jsVH2023-07-12_14h.40.03.csv')
