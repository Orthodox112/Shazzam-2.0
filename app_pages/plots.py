"""
plots.py
========
Matplotlib figure builders for the three visuals the project spec requires
in the Identify tab: the spectrogram, the constellation of peaks, and the
offset histogram that decides the match (Q3B: "showing the intermediate
steps"). Styled to match the app's light paper / deep-teal theme.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

BG = "#FAF8F3"
PANEL = "#FFFFFF"
TEAL = "#0E7C70"
TEXT = "#5B6A65"
GRID = "#E2DDD0"
BAR_DIM = "#D8D2C2"


def _style_axes(ax):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=TEXT, labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)
    ax.title.set_color(TEXT)


def plot_spectrogram(freq_axis, time_axis, S_db, title="Spectrogram", figsize=(6, 3.4)):
    fig, ax = plt.subplots(figsize=figsize, facecolor=BG)
    _style_axes(ax)
    im = ax.pcolormesh(
        time_axis, freq_axis, S_db, shading="auto", cmap="viridis", vmin=-80, vmax=0
    )
    ax.set_xlabel("time (s)", fontsize=9)
    ax.set_ylabel("frequency (Hz)", fontsize=9)
    ax.set_title(title, fontsize=10, loc="left")
    cbar = fig.colorbar(im, ax=ax, pad=0.02)
    cbar.ax.tick_params(colors=TEXT, labelsize=7)
    cbar.set_label("magnitude (dB)", color=TEXT, fontsize=8)
    fig.tight_layout()
    return fig


def plot_constellation(peaks_hz_sec, n_peaks=None, figsize=(6, 3.4)):
    fig, ax = plt.subplots(figsize=figsize, facecolor=BG)
    _style_axes(ax)
    if peaks_hz_sec:
        ts = [p[0] for p in peaks_hz_sec]
        fs = [p[1] for p in peaks_hz_sec]
        ax.scatter(ts, fs, s=6, color=TEAL, alpha=0.85, linewidths=0)
    ax.set_xlabel("time (s)", fontsize=9)
    ax.set_ylabel("frequency (Hz)", fontsize=9)
    label = f"{n_peaks} peaks" if n_peaks is not None else f"{len(peaks_hz_sec)} peaks"
    ax.set_title(label, fontsize=10, loc="right", color=TEAL)
    ax.grid(color=GRID, linewidth=0.5, alpha=0.5)
    fig.tight_layout()
    return fig


def plot_offset_histogram(histogram_dict, best_offset=None, hop_length=1024, sr=22050, figsize=(6, 2.6)):
    """
    histogram_dict : {offset_in_frames: vote_count} for the BEST candidate song.
    Renders Q3A's 'a true match lines them all up at a single offset' picture.
    """
    fig, ax = plt.subplots(figsize=figsize, facecolor=BG)
    _style_axes(ax)
    if histogram_dict:
        offsets = np.array(sorted(histogram_dict.keys()))
        counts = np.array([histogram_dict[o] for o in offsets])
        offsets_sec = offsets * hop_length / sr

        # Auto-scale bar width so bars are always visible regardless of x-axis span.
        # When a true match exists, most votes cluster at one offset — the bar must
        # be wide enough to see even when the axis spans 100+ seconds.
        if len(offsets_sec) == 1:
            # Single spike: zoom the axis in around it and use a fat bar
            center = offsets_sec[0]
            half_span = max(15.0, abs(center) * 0.3)
            ax.set_xlim(center - half_span, center + half_span)
            bar_width = half_span * 0.15
        else:
            data_span = float(offsets_sec[-1] - offsets_sec[0])
            natural_width = hop_length / sr * 0.9
            # Ensure bars are at least 1.5 % of the total data span
            bar_width = max(natural_width, data_span * 0.015, 0.5)

        colors = [TEAL if o == best_offset else BAR_DIM for o in offsets]
        ax.bar(offsets_sec, counts, width=bar_width, color=colors)

    ax.set_xlabel("offset (s)", fontsize=9)
    ax.set_ylabel("votes", fontsize=9)
    ax.set_title("offset histogram (best candidate)", fontsize=10, loc="left")
    fig.tight_layout()
    return fig


def plot_candidate_bars(candidate_scores, top_n=5, figsize=(6, 2.6)):
    fig, ax = plt.subplots(figsize=figsize, facecolor=BG)
    _style_axes(ax)
    top = candidate_scores[:top_n][::-1]
    if top:
        names = [n for n, _ in top]
        scores = [s for _, s in top]
        colors = [TEAL if i == len(top) - 1 else BAR_DIM for i in range(len(top))]
        ax.barh(names, scores, color=colors)
    ax.set_xlabel("votes", fontsize=9)
    fig.tight_layout()
    return fig
