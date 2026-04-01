"""
st.session_state.cm: Colormap
st.session_state.cm_name: 'cm' for custom cm, others for default Colormaps
st.session_state.list_rgb: list of rgb(hex)
st.session_state.num_div: number of rgb to create seamless colormap
st.session_state.num_cls: number of rgb to create graduated colormap
"""
import random

import streamlit as st
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib import colormaps
from matplotlib.figure import Figure
from matplotlib.colors import LinearSegmentedColormap, Colormap
import numpy as np
import pandas as pd


NUM_DIV_MAX = 12  # カスタムカラーマップで指定できる色の数の最大値


def plot_color_gradients(
        cmap_list: list
    ) -> Figure:
    """
    https://matplotlib.org/stable/users/explain/colors/colormaps.html
    """
    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))

    # Create figure and adjust figure height to number of colormaps
    nrows = len(cmap_list)
    figh = 0.35 + 0.15 + (nrows + (nrows - 1) * 0.1) * 0.22
    fig, axs = plt.subplots(nrows=nrows + 1, figsize=(6.4, figh))
    fig.subplots_adjust(top=1 - 0.35 / figh, bottom=0.15 / figh,
                        left=0.2, right=0.99)

    for ax, name in zip(axs, cmap_list):
        ax.imshow(gradient, aspect='auto', cmap=mpl.colormaps[name])
        ax.text(-0.01, 0.5, name, va='center', ha='right', fontsize=10,
                transform=ax.transAxes)

    # Turn off *all* ticks & spines, not just the ones with colormaps.
    for ax in axs:
        ax.set_axis_off()

    return fig


def create_initial_custom_cm() -> Colormap:
    """
    Return a colormap named 'cm'.
    The colormap is duraduated from white to a random color.
    """
    color_left = '#FFFFFF'
    color_right = random.choice(
        list(mcolors.TABLEAU_COLORS.values())
    )
    cm = LinearSegmentedColormap.from_list(
        name='cm',
        colors=[color_left, color_right]
    )
    st.session_state['cm_name'] = 'cm'

    return cm


def create_cm(
        list_rgb: list,
        cm_name='cm'
    ) -> Colormap:
    """
    Return a colormap. The colormap is created from the list of rgb.
    The name of colormap can be specified.
    """
    cm = LinearSegmentedColormap.from_list(
        name=cm_name,
        colors=list_rgb
    )
    return cm


def update_list_rgb(
        list_rgb: list,
        i_target: int,
        rgb_new: str
    ) -> list:
    """
    Replace the rgb on the target index with new rgb, and return the new list of rgb.
    """
    list_rgb_new = []
    for i, rgb in enumerate(list_rgb):
        if i == i_target:
            list_rgb_new.append(rgb_new)
        else:
            list_rgb_new.append(rgb)

    return list_rgb_new


def get_list_rgb(
        cm: Colormap,
        num_div: int
    ) -> list:
    """
    Return the list of rgbs(hex).
    The rgbs are the colors at the points divided by num_div on the colormap.
    """
    list_rgb = [mcolors.to_hex(cm(i / (num_div - 1))) for i in range(num_div)]
    return list_rgb


def create_colorbar(
        cm: Colormap,
        num_div: int,
        num_cls: int,
        cm_name: str
    ) -> Figure:
    """
    Return a figure that has two colorbars.
    The upper colorbar is seamless, and the bottom one is graduated.
    The number of xtick of seamless colorbar is specified by num_div if cm_name is 'cm'.
    The number of xtick of graduated colorbar is specified by num_cls.
    """
    fig, (ax1, ax2) = plt.subplots(nrows=2, figsize=(8, 1))

    # seamless colormap
    gradient = np.linspace(0, 1, 256)
    gradient_array = np.vstack((gradient, gradient))

    ax1.imshow(gradient_array, aspect='auto', cmap=cm)
    ax1.set_xticks(
        ticks=[round(i / (num_div - 1) * 256) for i in range(num_div)],
        labels=[f"{i+1}" for i in range(num_div)]
    )
    ax1.set_xlabel('Color', labelpad=-55)

    if cm_name == 'cm':
        ax1.tick_params(
            labelleft=False,
            left=False,
            labelbottom=False,
            bottom=False,
            labeltop=True,
            top=True
        )
    else:
        ax1.tick_params(
            labelleft=False,
            left=False,
            labelbottom=False,
            bottom=False
        )

    # graduated colormap
    gradient_cls = np.linspace(0, 1, num_cls)
    gradient_cls_array = np.vstack((gradient_cls, gradient_cls))
    cm_cls = plt.get_cmap(cm, num_cls)

    ax2.imshow(gradient_cls_array, aspect='auto', cmap=cm_cls)
    ax2.set_xlabel('Class')
    ax2.set_xticks(
        ticks=[i for i in range(num_cls)],
        labels=[f"{i+1}" for i in range(num_cls)]
    )
    ax2.tick_params(
        labelleft=False,
        left=False,
        labelbottom=True,
        bottom=False
    )

    return fig


def create_rgb_table(
        cm: Colormap,
        num_colors: int,
        name_index: str
    ) -> pd.DataFrame:
    """
    Return a dataframe that has rgb infomation.
    The rgbs are expressed by hex and RGB.
    """
    data = []
    for i in range(num_colors):
        rgb = mcolors.to_hex(cm(i / (num_colors - 1)))
        r, g, b = mcolors.to_rgb(cm(i / (num_colors - 1)))
        data.append(
            {
                name_index: i + 1,
                'RBG': rgb.upper(),
                'R': round(r * 256),
                'G': round(g * 256),
                'B': round(b * 256)
            }
        )
    df = pd.DataFrame(data)
    df = df.set_index(name_index, drop=True)

    return df


def callback_update_cm(
        list_rgb: list,
        i_target: int,
        num_div: int
    ) -> None:
    """
    Callback function set on st.color_picker.
    The widget has the key of 'rgb_new_{i_target}'.
    Update colormap and some st.session_state.
    """
    rgb_new = st.session_state[f"rgb_new_{i_target}"]
    list_rgb_new = update_list_rgb(
        list_rgb=list_rgb,
        i_target=i_target,
        rgb_new=rgb_new
    )
    cm_new = create_cm(
        list_rgb=list_rgb_new
    )
    st.session_state['num_div'] = num_div
    st.session_state['list_rgb'] = list_rgb_new
    st.session_state['cm'] = cm_new


def callback_delete_rgb_from_cm(
        list_rgb: list,
        i_target: int,
        num_div: int
    ) -> None:
    """
    Callback function.
    Delete one color from the list of rgbs.
    Update colormap and some st.session_state.
    """
    if num_div == 2:
        st.warning('色を削除できません')
        st.session_state['num_div'] = 2
        return

    list_rgb_new = list_rgb
    del list_rgb_new[i_target]

    cm_new = create_cm(
        list_rgb=list_rgb_new
    )
    st.session_state['num_div'] = num_div - 1
    st.session_state['list_rgb'] = list_rgb_new
    st.session_state['cm'] = cm_new


def callback_add_rgb_to_cm(
        list_rgb: list,
        i_target: int,
        num_div: int
    ) -> None:
    """
    Callback function.
    Add one color to the list of rgbs.
    Update colormap and some st.session_state.
    """
    if num_div == NUM_DIV_MAX:
        st.warning('色を追加できません')
        st.session_state['num_div'] = num_div
        return

    list_rgb_new = list_rgb
    rgb_new = list_rgb[i_target]
    list_rgb_new.insert(i_target, rgb_new)
    cm_new = create_cm(
        list_rgb=list_rgb_new
    )
    st.session_state['num_div'] = num_div + 1
    st.session_state['list_rgb'] = list_rgb_new
    st.session_state['cm'] = cm_new


def callback_reverse_cm(
        list_rgb: list,
        cm_name: str,
        num_div: int
    ) -> None:
    """
    Callback function.
    Reverse a colomap and update some st.session_state.
    """
    list_rgb_new = list_rgb[::-1]

    if cm_name == 'cm':
        cm_name_new = cm_name
        cm_new = create_cm(
            list_rgb=list_rgb_new,
            cm_name=cm_name
        )
    else:
        if cm_name.endswith('_r'):
            cm_name_new = cm_name.removesuffix('_r')
        else:
            cm_name_new = cm_name + '_r'

        cm_new = plt.get_cmap(cm_name_new)

    st.session_state['num_div'] = num_div
    st.session_state['list_rgb'] = list_rgb_new
    st.session_state['cm_name'] = cm_name_new
    st.session_state['cm'] = cm_new


def main():
    st.set_page_config(
        page_title='ColorGraduator',
        page_icon='☕',
        layout='wide'
    )
    st.title('ColorGraduator')
    st.write('段階的グラデーション作成アプリ')

    if 'cm' not in st.session_state:
        # On app startup
        with st.container(border=True):
            st.markdown(':memo: 基本のカラーマップを指定（カスタム or プリセット）')

            col1, col2 = st.columns([0.4, 0.6])
            with col1:
                with st.form(key='form_custom', border=True):
                    st.markdown('カスタム')
                    st.number_input(
                        label=f"指定する色の数 (2 ~ {NUM_DIV_MAX})",
                        min_value=2,
                        max_value=NUM_DIV_MAX,
                        value=4,
                        key='num_div'
                    )
                    st.form_submit_button(
                        label='決定',
                        on_click=lambda :st.session_state.update(
                            cm=create_initial_custom_cm()
                        )
                    )
            with col2:
                with st.form(key='form_preset', border=True):
                    st.markdown('プリセット')

                    cmap_list = list(colormaps)
                    cmap_list = [
                        colormap for colormap in cmap_list if not colormap.endswith('_r')
                    ]

                    st.selectbox(
                        label='名前を選択',
                        options=sorted(cmap_list, key=lambda x: x.upper()),
                        index=random.choice([i for i in range(len(cmap_list))]),
                        key='cm_name'
                    )
                    st.form_submit_button(
                        label='決定',
                        on_click=lambda :st.session_state.update(
                            cm=plt.get_cmap(st.session_state['cm_name'])
                        )
                    )

                    fig_cmap = plot_color_gradients(
                        cmap_list=cmap_list
                    )
                    st.pyplot(fig_cmap)
    else:
        # After colormap is specified
        st.session_state['list_rgb'] = get_list_rgb(
            cm=st.session_state['cm'],
            num_div=st.session_state['num_div']
        )
        if 'num_cls' not in st.session_state:
            st.session_state['num_cls'] = 6

        cm = st.session_state['cm']

        st.session_state['cm_name'] = cm.name

        list_rgb = st.session_state['list_rgb']
        num_div = st.session_state['num_div']
        num_cls = st.session_state['num_cls']

        if cm.name == 'cm':
            # For custom colormap
            with st.container(border=True):
                st.markdown('カラーマップ: カスタム')

                cols = st.columns(num_div)

                for i, col in enumerate(cols):
                    with col:
                        rgb = mcolors.to_hex(
                            st.session_state['cm'](i / (num_div - 1))
                        )
                        st.button(
                            label=':material/remove:',
                            key=f"button_del_{i}",
                            args=(list_rgb, i, num_div),
                            on_click=callback_delete_rgb_from_cm
                        )
                        st.button(
                            label=':material/add:',
                            key=f"button_copy_{i}",
                            args=(list_rgb, i, num_div),
                            on_click=callback_add_rgb_to_cm
                        )
                        st.color_picker(
                            label=f"Color {i+1}",
                            value=rgb,
                            key=f"rgb_new_{i}",
                            args=(list_rgb, i, num_div),
                            on_change=callback_update_cm
                        )
                st.button(
                    label='反転',
                    args=(list_rgb, cm.name, num_div),
                    on_click=callback_reverse_cm
                )
        else:
            # For preset colormap
            with st.container(border=True):
                st.markdown(f"カラーマップ: {cm.name}")
                st.button(
                    label='反転',
                    args=(list_rgb, cm.name, num_div),
                    on_click=callback_reverse_cm
                )

        fig = create_colorbar(
            cm=cm,
            num_div=num_div,
            num_cls=num_cls,
            cm_name=cm.name
        )
        st.pyplot(fig)

        col1, col2 = st.columns(2)
        with col1:
            # Class settings and display
            with st.container(border=True):
                st.markdown(':memo: クラス数を指定')
                st.number_input(
                    label='_',
                    min_value=2,
                    max_value=256,
                    key='num_cls',
                    label_visibility='collapsed',
                    on_change=lambda :st.session_state.update(
                        num_div=num_div
                    )
                )
                df_cls = create_rgb_table(
                    cm=cm,
                    num_colors=num_cls,
                    name_index='Class'
                )
                st.markdown('クラスのRGB')
                st.dataframe(df_cls)
        with col2:
            # Download
            with st.container(border=True):
                st.markdown(':sparkles: RGB をダウンロード')

                col2_1, col2_2 = st.columns(2)
                with col2_1:
                    st.markdown('クラスの色')
                    st.download_button(
                        label='Download',
                        file_name='rgb_class.csv',
                        data=df_cls.to_csv(),
                        on_click='ignore',
                        key='download_button_class'
                    )
                with col2_2:
                    if st.session_state['cm_name'] == 'cm':
                        st.markdown('指定の色')
                        df_div = create_rgb_table(
                            cm=cm,
                            num_colors=num_div,
                            name_index='Color'
                        )
                        st.download_button(
                            label='Download',
                            file_name='rgb_color.csv',
                            data=df_div.to_csv(),
                            on_click='ignore',
                            key='download_button_colors'
                        )

            st.markdown("""
            * ブラウザ更新でリセットできます
            * RGB は 24bitカラー の 16 進数と 10 進数で表記しています
            """)


if __name__ == '__main__':
    main()
