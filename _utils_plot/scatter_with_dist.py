from _utils_import import np, plt
import _utils_plot

def plot_scatter_with_dist(
    x, y, x_label="x", y_label="y",
    title="title",
    save=False,
    file_path_save=None,
    color=(0.0, 0.0, 0.0, 1.0),
):
    import matplotlib.gridspec as gridspec
    from scipy import stats
    fig = plt.figure(figsize=(10, 8))
    fig.suptitle(title, fontsize=16)
    gs = gridspec.GridSpec(4, 4)

    # Set up the axes
    ax_scatter = plt.subplot(gs[1:4, 0:3])  # Scatter plot in the bottom-left
    ax_x_dist = plt.subplot(gs[0, 0:3])      # X distribution on top
    ax_y_dist = plt.subplot(gs[1:4, 3])      # Y distribution on right

    # Create the scatter plot
    ax_scatter.scatter(x, y, alpha=0.6, c=color)
    ax_scatter.set_xlabel(x_label)
    ax_scatter.set_ylabel(y_label)

    try:
        ax_x_dist.hist(x, bins=30, density=True, alpha=0.7)
        x_grid = np.linspace(min(x), max(x), 100)
        x_kde = stats.gaussian_kde(x)
        ax_x_dist.plot(x_grid, x_kde(x_grid), 'r-')
        ax_x_dist.set_xlim(ax_scatter.get_xlim())
        ax_x_dist.set_yticks([])
    except Exception: pass
    try:
        ax_y_dist.hist(y, bins=30, density=True, alpha=0.7, orientation='horizontal')
        y_grid = np.linspace(min(y), max(y), 100)
        y_kde = stats.gaussian_kde(y)
        ax_y_dist.plot(y_kde(y_grid), y_grid, 'r-')
        ax_y_dist.set_ylim(ax_scatter.get_ylim())
        ax_y_dist.set_xticks([])
    except Exception: pass

    plt.tight_layout()
    # plt.show()
    if save:
        _utils_plot.save_fig_for_plt(file_path_save)
    else:
        return fig

if __name__ == "__main__":
    # Generate some sample data
    np.random.seed(42)
    x = np.random.normal(0, 1, 1000)
    y = x * 0.5 + np.random.normal(0, 1, 1000)