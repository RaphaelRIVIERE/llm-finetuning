import pandas as pd
import seaborn as sns
import numpy as np
from matplotlib.axes import Axes
from matplotlib.container import BarContainer


def _apply_formatting(
    ax: Axes,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    xrotation: int = 0,
    yrotation: int = 0,
    grid: bool = False,
    legend_title: str | None = None,
    show_legend: bool = False,
    xticklabels=None,
    subtitle: str | None = None,
    suptitle_y: float = 0.92,
):
    """Applique le formatage de base à un axe matplotlib."""
    if title:
        if subtitle:
            ax.set_title(title, fontsize=14, fontweight='bold', y=1.02)
        else:
            ax.set_title(title, fontsize=14, fontweight='bold')
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=12)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=12)
    if subtitle:
        ax.figure.suptitle(subtitle, fontsize=11, y=suptitle_y, style='italic')

    ax.tick_params(axis='x', rotation=xrotation)
    ax.tick_params(axis='y', rotation=yrotation)

    if grid:
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        ax.set_axisbelow(True)

    if show_legend and ax.get_legend_handles_labels()[0]:
        ax.legend(title=legend_title, loc='best', fontsize=10)
    elif (legend := ax.get_legend()) is not None:
        legend.remove()

    if xticklabels is not None:
        ax.set_xticks(ax.get_xticks(), labels=xticklabels, fontsize=11)


def _annotate_bars(ax: Axes, fmt: str = '{:.2f}', ylim_margin: float = 1.15):
    """Ajoute les valeurs au-dessus des barres."""
    for container in ax.containers:
        if isinstance(container, BarContainer):
            ax.bar_label(container, fmt=fmt, padding=3, fontsize=10)

    ymin, ymax = ax.get_ylim()
    if ymax > 0:
        ax.set_ylim(ymin, ymax * ylim_margin)


def create_barplot(
    df: pd.DataFrame, ax: Axes, x: str, y: str,
    hue: str | None = None,
    title: str | None = None, xlabel: str | None = None, ylabel: str | None = None,
    subtitle: str | None = None,
    xrotation: int = 45, palette=None,
    legend_title: str | None = None, show_legend: bool = False,
    annot: bool = True, fmt: str = '{:.2f}',
    alpha: float = 1.0, edgecolor=None, linewidth: float = 0.0,
    width: float = 0.8, errorbar=None, estimator=np.mean,
    ylim_margin: float = 1.15, xticklabels=None, grid: bool = False,
):
    """Crée un barplot (valeurs agrégées par catégorie)."""
    sns.barplot(data=df, x=x, y=y, hue=hue, palette=palette, ax=ax,
                alpha=alpha, edgecolor=edgecolor, linewidth=linewidth,
                width=width, errorbar=errorbar, estimator=estimator)

    _apply_formatting(
        ax, title=title, xlabel=xlabel, ylabel=ylabel, subtitle=subtitle,
        xrotation=xrotation, grid=grid, legend_title=legend_title,
        show_legend=show_legend, xticklabels=xticklabels,
    )

    if annot:
        _annotate_bars(ax, fmt=fmt, ylim_margin=ylim_margin)


def create_histplot(
    df: pd.DataFrame, ax: Axes, x: str,
    hue: str | None = None,
    title: str | None = None, xlabel: str | None = None, ylabel: str | None = None,
    subtitle: str | None = None,
    xrotation: int = 0, palette=None,
    legend_title: str | None = None, show_legend: bool = True,
    bins: int | str = 50, alpha: float = 0.6,
    stat: str = 'count', kde: bool = False,
    multiple: str = 'layer',
    annot: bool = False, fmt: str = '{:.0f}',
    grid: bool = False, xticklabels=None,
):
    """Crée un histogramme (distribution d'une variable numérique)."""
    sns.histplot(
        data=df, x=x, hue=hue, palette=palette, ax=ax,
        bins=bins, alpha=alpha, stat=stat, kde=kde, multiple=multiple,
    )

    _apply_formatting(
        ax, title=title, xlabel=xlabel, ylabel=ylabel, subtitle=subtitle,
        xrotation=xrotation, grid=grid, legend_title=legend_title,
        show_legend=show_legend, xticklabels=xticklabels,
    )

    if annot:
        _annotate_bars(ax, fmt=fmt)


def create_heatmap(
    df: pd.DataFrame, ax: Axes,
    annot: bool = True,
    # fmt suit la syntaxe Python format spec (ex: '.2f', 'd'), pas '{:.2f}'
    fmt: str = '.2f',
    cmap: str = 'coolwarm',
    title: str | None = None, xlabel: str | None = None, ylabel: str | None = None,
    subtitle: str | None = None,
    xrotation: int = 45, yrotation: int = 0,
    linewidths: float = 0.5, linecolor: str = 'white',
    vmin=None, vmax=None, center=None,
    cbar: bool = True, square: bool = False, mask=None,
    grid: bool = False, show_legend: bool = False, legend_title: str | None = None,
    xticklabels=None,
):
    """Crée une heatmap."""
    sns.heatmap(data=df, ax=ax, annot=annot, fmt=fmt, cmap=cmap,
                linewidths=linewidths, linecolor=linecolor,
                vmin=vmin, vmax=vmax, center=center,
                cbar=cbar, square=square, mask=mask)

    _apply_formatting(
        ax, title=title, xlabel=xlabel, ylabel=ylabel, subtitle=subtitle,
        xrotation=xrotation, yrotation=yrotation,
        grid=grid, show_legend=show_legend, legend_title=legend_title,
        xticklabels=xticklabels,
    )
