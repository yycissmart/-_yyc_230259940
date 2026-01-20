import numpy as np
import streamlit as st

st.set_page_config(page_title="光学常用公式计算器", page_icon="🔬", layout="centered")

st.title("🔬 光学常用公式计算器")
st.caption("激光与光学常用快速估算：能量、光斑、焦深、发散角、光栅、功率密度、光程差/延迟等。")

C0 = 299_792_458.0  # m/s 真空光速

# -------------------------
# 单位换算
# -------------------------
def to_si(value, unit):
    scale = {
        "W": 1.0, "mW": 1e-3, "kW": 1e3,
        "Hz": 1.0, "kHz": 1e3, "MHz": 1e6, "GHz": 1e9,
        "J": 1.0, "mJ": 1e-3, "uJ": 1e-6, "nJ": 1e-9,
        "s": 1.0, "ms": 1e-3, "us": 1e-6, "ns": 1e-9, "ps": 1e-12, "fs": 1e-15,
        "m": 1.0, "mm": 1e-3, "um": 1e-6, "nm": 1e-9,
        "deg": np.pi/180.0, "rad": 1.0,
        "cm2": 1e-4, "mm2": 1e-6, "um2": 1e-12, "m2": 1.0,
        "lines/mm": 1e3, "lines/m": 1.0,  # 光栅线密度 -> 1/m
    }
    return value * scale[unit]

def format_eng(x, unit):
    if x == 0 or np.isnan(x) or np.isinf(x):
        return f"{x} {unit}"
    exp = int(np.floor(np.log10(abs(x)) / 3) * 3)
    exp = max(min(exp, 12), -15)
    x_scaled = x / (10 ** exp)
    prefix = {-15:"f",-12:"p",-9:"n",-6:"µ",-3:"m",0:"",3:"k",6:"M",9:"G",12:"T"}[exp]
    return f"{x_scaled:.4g} {prefix}{unit}"

def clamp01(x):
    return max(0.0, min(1.0, x))

# -------------------------
# 侧边栏
# -------------------------
st.sidebar.header("功能选择")
mode = st.sidebar.radio(
    "选择你要计算的内容：",
    [
        "单脉冲能量",
        "聚焦光斑",
        "焦深 / 瑞利长度",
        "峰值功率",
        "角度制 ↔ 弧度制",
        "光栅公式",
        "激光光斑功率密度",
        "光程差 ↔ 延迟时间",
        "高斯光束发散角",
    ],
)

st.sidebar.markdown("---")
st.sidebar.caption("建议：所有输入支持常用单位；每个页面底部提供公式与说明。")

# =========================================================
# 1) 单脉冲能量
# =========================================================
if mode == "单脉冲能量":
    st.subheader("✅ 单脉冲能量（由平均功率与重复频率）")

    c1, c2 = st.columns(2)
    with c1:
        p_val = st.number_input("平均功率 P_avg", min_value=0.0, value=1.0, step=0.1)
        p_unit = st.selectbox("功率单位", ["W", "mW", "kW"], index=0)
    with c2:
        f_val = st.number_input("重复频率 f_rep", min_value=0.0, value=100.0, step=10.0)
        f_unit = st.selectbox("频率单位", ["Hz", "kHz", "MHz", "GHz"], index=1)

    P = to_si(p_val, p_unit)
    f = to_si(f_val, f_unit)

    if f <= 0:
        st.error("重复频率必须大于 0。")
    else:
        E = P / f
        st.success(f"单脉冲能量 E ≈ {format_eng(E, 'J')}")

    st.markdown("---")
    st.markdown("### 计算公式与原理说明")
    st.latex(r"E=\frac{P_{\mathrm{avg}}}{f_{\mathrm{rep}}}")
    st.markdown(
    "- 平均功率 $P_{avg}$ 表示单位时间内输出的能量。\n"
    "- 重复频率 $f_{rep}$ 表示每秒脉冲个数。\n"
    "- 因此单个脉冲能量等于“每秒能量”除以“每秒脉冲数”。\n"
    "- 若存在门控/占空比/脉冲串结构，需要先换算到实际脉冲串内的平均功率。"
    )

# =========================================================
# 2) 聚焦光斑（衍射极限）
# =========================================================
elif mode == "聚焦光斑":
    st.subheader("✅ 聚焦光斑（衍射极限估算）")

    spot_def = st.radio(
        "光斑口径（常用定义）：",
        ["Airy 圆盘直径（第一零点）", "高斯 1/e² 半径 w0（工程常用近似）"],
        horizontal=True
    )

    c1, c2 = st.columns(2)
    with c1:
        lam_val = st.number_input("波长 λ", min_value=0.0, value=1030.0, step=10.0)
        lam_unit = st.selectbox("波长单位", ["nm", "um", "mm", "m"], index=0)
    with c2:
        na_val = st.number_input("数值孔径 NA", min_value=0.0, value=0.10, step=0.01, format="%.3f")

    lam = to_si(lam_val, lam_unit)
    NA = na_val

    if NA <= 0:
        st.error("NA 必须大于 0。")
    else:
        airy_d = 1.22 * lam / NA
        w0 = lam / (np.pi * NA)

        if spot_def == "Airy 圆盘直径（第一零点）":
            st.success(f"Airy 圆盘直径 d ≈ {format_eng(airy_d, 'm')}")
        else:
            st.success(f"高斯束腰 1/e² 半径 w0 ≈ {format_eng(w0, 'm')}")

        st.info("提示：若光束质量不是理想 TEM00，可近似乘以 M² 修正（光斑变大）。")

    st.markdown("---")
    st.markdown("### 计算公式与原理说明")
    st.latex(r"d_{\mathrm{Airy}}\approx \frac{1.22\,\lambda}{NA}")
    st.latex(r"w_0 \approx \frac{\lambda}{\pi\,NA}")
    st.markdown(
    "- 对圆形孔径成像系统，衍射形成 Airy 图样，第一暗环对应半径 "
    r"$0.61\,\lambda/NA$，直径为 $1.22\,\lambda/NA$。\n"
    "- 高斯束聚焦的束腰 $w_0$ 常用工程近似为 "
    r"$w_0\approx \lambda/(\pi\,NA)$；严格值会受入瞳填充、像差、$M^2$ 等影响。"
    )

# =========================================================
# 3) 焦深 / 瑞利长度
# =========================================================
elif mode == "焦深 / 瑞利长度":
    st.subheader("✅ 焦深 / 瑞利长度（Rayleigh range）")

    input_mode = st.radio(
        "输入方式：",
        ["直接输入束腰半径 w0", "由波长 λ 与 NA 估算 w0（w0=λ/(πNA)）"],
        horizontal=True
    )

    c1, c2 = st.columns(2)
    with c1:
        lam_val = st.number_input("波长 λ", min_value=0.0, value=1030.0, step=10.0, key="lam_fd")
        lam_unit = st.selectbox("波长单位", ["nm", "um", "mm", "m"], index=0, key="lamu_fd")
    lam = to_si(lam_val, lam_unit)

    if input_mode == "直接输入束腰半径 w0":
        w0_val = st.number_input("束腰半径 w0", min_value=0.0, value=5.0, step=0.5)
        w0_unit = st.selectbox("w0 单位", ["um", "mm", "m", "nm"], index=0)
        w0 = to_si(w0_val, w0_unit)
    else:
        na_val = st.number_input("数值孔径 NA", min_value=0.0, value=0.10, step=0.01, format="%.3f")
        if na_val <= 0:
            st.error("NA 必须大于 0。")
            st.stop()
        w0 = lam / (np.pi * na_val)
        st.write(f"由 NA 估算得到 w0 ≈ {format_eng(w0, 'm')}")

    if lam <= 0 or w0 <= 0:
        st.error("λ 与 w0 必须都大于 0。")
    else:
        zR = np.pi * (w0 ** 2) / lam
        confocal = 2 * zR
        st.success(f"瑞利长度 z_R ≈ {format_eng(zR, 'm')}")
        st.success(f"焦深（常用 2z_R）≈ {format_eng(confocal, 'm')}")

    st.markdown("---")
    st.markdown("### 计算公式与原理说明")
    st.latex(r"z_R=\frac{\pi w_0^2}{\lambda}")
    st.latex(r"\mathrm{DOF}\ \approx 2z_R")
    st.markdown(
    "- 高斯光束在束腰附近的传播由瑞利长度 $z_R$ 描述。\n"
    "- 在 $z=z_R$ 处，光束半径增大到 $w(z)=\sqrt{2}\,w_0$。\n"
    "- 因此常用共焦参数 $2z_R$ 作为“焦深”的工程定义（不同领域也可能用其他阈值定义焦深）。"
    )

# =========================================================
# 4) 峰值功率
# =========================================================
elif mode == "峰值功率":
    st.subheader("✅ 峰值功率估算（由脉冲能量与脉宽）")

    c1, c2 = st.columns(2)
    with c1:
        e_val = st.number_input("单脉冲能量 E", min_value=0.0, value=10.0, step=1.0)
        e_unit = st.selectbox("能量单位", ["J", "mJ", "uJ", "nJ"], index=2)
    with c2:
        t_val = st.number_input("脉宽 τ", min_value=0.0, value=300.0, step=10.0)
        t_unit = st.selectbox("脉宽单位", ["s", "ms", "us", "ns", "ps", "fs"], index=4)

    shape = st.radio(
        "脉冲形状修正（可选）：",
        ["不修正（矩形等效）", "高斯脉冲（输入为强度 FWHM）"],
        horizontal=True
    )

    E = to_si(e_val, e_unit)
    tau = to_si(t_val, t_unit)

    if tau <= 0:
        st.error("脉宽必须大于 0。")
    else:
        if shape == "不修正（矩形等效）":
            Pp = E / tau
            st.success(f"峰值功率 P_peak ≈ {format_eng(Pp, 'W')}")
        else:
            corr = np.sqrt(np.pi / (4.0 * np.log(2.0)))
            Pp = E / (tau * corr)
            st.success(f"峰值功率 P_peak ≈ {format_eng(Pp, 'W')}")

    st.markdown("---")
    st.markdown("### 计算公式与原理说明")
    st.latex(r"P_{\mathrm{peak}}\approx \frac{E}{\tau}")
    st.latex(
        r"\text{若为高斯强度脉冲(FWHM)}:\quad "
        r"P_{\mathrm{peak}}=\frac{E}{\tau_{\mathrm{FWHM}}\sqrt{\pi/(4\ln2)}}"
    )
    st.markdown(
    "- 矩形等效是假设脉冲在触发时功率恒定。\n"
    "- 若脉冲更接近高斯形状且输入的是强度 FWHM，则需用系数把面积（能量）与峰值联系起来。"
    )

# =========================================================
# 5) 角度制 ↔ 弧度制
# =========================================================
elif mode == "角度制 ↔ 弧度制":
    st.subheader("✅ 角度制与弧度制转换")

    submode = st.radio("转换方向：", ["度 → 弧度", "弧度 → 度"], horizontal=True)

    if submode == "度 → 弧度":
        deg = st.number_input("角度（deg）", value=30.0, step=1.0)
        rad = np.deg2rad(deg)
        st.success(f"{deg:.6g}° = {rad:.6g} rad")
    else:
        rad = st.number_input("弧度（rad）", value=np.pi/6, step=0.1, format="%.6f")
        deg = np.rad2deg(rad)
        st.success(f"{rad:.6g} rad = {deg:.6g}°")

    st.markdown("---")
    st.markdown("### 计算公式与原理说明")
    st.latex(r"\theta_{\mathrm{rad}}=\theta_{\mathrm{deg}}\cdot\frac{\pi}{180}")
    st.latex(r"\theta_{\mathrm{deg}}=\theta_{\mathrm{rad}}\cdot\frac{180}{\pi}")
    st.markdown(
        "- 弧度定义：弧长等于半径时对应的角度为 $1\\ \\mathrm{rad}$。\n"
        "- 一周为 $2\\pi$ rad，对应 $360^\\circ$，据此得到换算关系。"
    )

# =========================================================
# 6) 光栅公式
# =========================================================
elif mode == "光栅公式":
    st.subheader("✅ 光栅公式（衍射角、线密度、级次）")

    st.write("采用反射/透射光栅的标量光栅方程（入射角与衍射角相对光栅法线测量）：")
    st.caption("注意符号约定很多，本工具用最常见形式：mλ = d (sinθ_i + sinθ_m)。")

    calc_mode = st.radio(
        "你要解哪个量？",
        ["求衍射角 θ_m", "求线密度（lines/mm）", "求可实现的最高级次 |m|max（粗估）"],
        horizontal=True
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        lam_val = st.number_input("波长 λ", min_value=0.0, value=532.0, step=1.0)
        lam_unit = st.selectbox("λ 单位", ["nm", "um", "mm", "m"], index=0)
    with c2:
        theta_i_val = st.number_input("入射角 θ_i（相对法线）", value=0.0, step=1.0)
        theta_i_unit = st.selectbox("θ_i 单位", ["deg", "rad"], index=0)
    with c3:
        m = st.number_input("衍射级次 m（整数）", value=1, step=1)

    lam = to_si(lam_val, lam_unit)
    theta_i = to_si(theta_i_val, theta_i_unit)

    if calc_mode == "求衍射角 θ_m":
        c4, c5 = st.columns(2)
        with c4:
            N_val = st.number_input("线密度 N", min_value=0.0, value=1200.0, step=10.0)
            N_unit = st.selectbox("N 单位", ["lines/mm", "lines/m"], index=0)
        with c5:
            out_unit = st.selectbox("输出角度单位", ["deg", "rad"], index=0)

        N = to_si(N_val, N_unit)      # 1/m
        if N <= 0:
            st.error("线密度必须 > 0。")
        else:
            d = 1.0 / N  # m
            rhs = (m * lam / d) - np.sin(theta_i)  # sin(theta_m)
            if rhs < -1 or rhs > 1:
                st.error("无实数解：该级次在此入射角/光栅常数下不满足 |sinθ_m|≤1。")
            else:
                theta_m = np.arcsin(rhs)
                if out_unit == "deg":
                    st.success(f"衍射角 θ_m ≈ {np.rad2deg(theta_m):.6g}°")
                else:
                    st.success(f"衍射角 θ_m ≈ {theta_m:.6g} rad")

    elif calc_mode == "求线密度（lines/mm）":
        c4, c5 = st.columns(2)
        with c4:
            theta_m_val = st.number_input("衍射角 θ_m（相对法线）", value=30.0, step=1.0)
            theta_m_unit = st.selectbox("θ_m 单位", ["deg", "rad"], index=0)
        with c5:
            out = st.selectbox("输出线密度单位", ["lines/mm", "lines/m"], index=0)

        theta_m = to_si(theta_m_val, theta_m_unit)
        denom = np.sin(theta_i) + np.sin(theta_m)
        if abs(denom) < 1e-15:
            st.error("sinθ_i + sinθ_m 过小，无法求解（分母接近 0）。")
        else:
            d = (m * lam) / denom
            if d <= 0:
                st.error("计算得到 d ≤ 0，通常意味着角度/级次符号约定不一致。请检查输入。")
            else:
                N = 1.0 / d  # lines/m
                if out == "lines/mm":
                    st.success(f"线密度 N ≈ {N/1e3:.6g} lines/mm")
                else:
                    st.success(f"线密度 N ≈ {N:.6g} lines/m")

    else:  # 粗估 |m|max
        c4, = st.columns(1)
        N_val = st.number_input("线密度 N", min_value=0.0, value=1200.0, step=10.0)
        N_unit = st.selectbox("N 单位", ["lines/mm", "lines/m"], index=0, key="Nmax_unit")
        N = to_si(N_val, N_unit)
        if N <= 0:
            st.error("线密度必须 > 0。")
        else:
            d = 1.0 / N
            # 要有解需 |sinθ_m|<=1，即 rhs in [-1,1]，rhs = mλ/d - sinθ_i
            # 粗估：mλ/d ≲ 1 + |sinθ_i| => |m|max ≈ d(1+|sinθ_i|)/λ
            mmax = int(np.floor(d * (1.0 + abs(np.sin(theta_i))) / lam)) if lam > 0 else 0
            st.success(f"粗估可实现最高级次 |m|max ≈ {mmax}")
            st.caption("这是不指定衍射角范围的“存在解”粗估；实际还会受效率、闪耀角、孔径与像差等影响。")

    st.markdown("---")
    st.markdown("### 计算公式与原理说明")
    st.latex(r"m\lambda=d\left(\sin\theta_i+\sin\theta_m\right)")
    st.markdown(
        "- 光栅相邻刻线间距为 $d$。\n"
        "- 相邻刻线出射光的相位差由几何路径差决定；当路径差满足 $m\\lambda$ 的整数倍时发生相长干涉，形成第 $m$ 级衍射主极大。\n"
        "- 不同教材/软件对角度正负、反射/透射的符号约定不同；若你发现求得 $d<0$ 或无解，请优先检查角度定义与级次符号。"
    )

# =========================================================
# 7) 激光光斑功率密度（平均功率密度）
# =========================================================
elif mode == "激光光斑功率密度":
    st.subheader("✅ 激光光斑功率密度估算（平均）")

    st.write("给定平均功率与光斑尺寸，估算平均功率密度（W/面积）。")
    st.caption("若要峰值强度（脉冲激光更常用），请结合“峰值功率”与光斑模型计算。")

    c1, c2 = st.columns(2)
    with c1:
        p_val = st.number_input("平均功率 P_avg", min_value=0.0, value=1.0, step=0.1)
        p_unit = st.selectbox("功率单位", ["W", "mW", "kW"], index=0, key="pd_punit")
    with c2:
        model = st.radio("光斑模型：", ["圆形均匀（顶帽）", "高斯（给 1/e² 半径 w）"], horizontal=True)

    P = to_si(p_val, p_unit)

    if model == "圆形均匀（顶帽）":
        c3, c4 = st.columns(2)
        with c3:
            r_val = st.number_input("光斑半径 r", min_value=0.0, value=50.0, step=1.0)
            r_unit = st.selectbox("r 单位", ["um", "mm", "m", "nm"], index=0)
        with c4:
            out = st.selectbox("输出单位", ["W/m²", "W/cm²"], index=1)

        r = to_si(r_val, r_unit)
        if r <= 0:
            st.error("半径必须 > 0。")
        else:
            A = np.pi * r**2
            I = P / A  # W/m^2
            if out == "W/cm²":
                st.success(f"平均功率密度 I ≈ {(I/1e4):.4g} W/cm²")
            else:
                st.success(f"平均功率密度 I ≈ {I:.4g} W/m²")

    else:  # Gaussian with 1/e^2 radius w
        c3, c4 = st.columns(2)
        with c3:
            w_val = st.number_input("1/e² 半径 w", min_value=0.0, value=50.0, step=1.0)
            w_unit = st.selectbox("w 单位", ["um", "mm", "m", "nm"], index=0, key="pd_wunit")
        with c4:
            out = st.selectbox("输出单位", ["W/m²", "W/cm²"], index=1, key="pd_out2")

        w = to_si(w_val, w_unit)
        if w <= 0:
            st.error("半径必须 > 0。")
        else:
            # 高斯强度分布 I(r)=I0 exp(-2r^2/w^2)，总功率 P = (pi w^2 / 2)*I0
            I0 = 2 * P / (np.pi * w**2)  # 峰值强度(平均功率对应的峰值)
            I_avg_over_disk = P / (np.pi * w**2)  # 作为一个“特征平均”也有人用
            if out == "W/cm²":
                st.success(f"高斯峰值功率密度 I0 ≈ {(I0/1e4):.4g} W/cm²")
                st.write(f"（参考：特征平均 P/(πw²) ≈ {(I_avg_over_disk/1e4):.4g} W/cm²）")
            else:
                st.success(f"高斯峰值功率密度 I0 ≈ {I0:.4g} W/m²")
                st.write(f"（参考：特征平均 P/(πw²) ≈ {I_avg_over_disk:.4g} W/m²）")

    st.markdown("---")
    st.markdown("### 计算公式与原理说明")
    st.latex(r"\text{顶帽(均匀圆斑)}:\quad I=\frac{P}{A}=\frac{P}{\pi r^2}")
    st.latex(
        r"\text{高斯(1/e}^2\text{半径 }w):\quad "
        r"I(r)=I_0 e^{-2r^2/w^2},\ \ P=\frac{\pi w^2}{2}I_0"
    )
    st.latex(r"\Rightarrow\ I_0=\frac{2P}{\pi w^2}")
    st.markdown(
        "- 顶帽模型假设光斑内功率均匀分布，适用于近似平顶整形光。\n"
        "- 高斯模型适用于 TEM$_{00}$ 近似；峰值强度 $I_0$ 与总功率 $P$ 的关系由面积积分得到。\n"
        "- 若是脉冲激光且关注瞬时峰值强度，应先由脉冲能量/脉宽得到峰值功率，再代入强度公式。"
    )

# =========================================================
# 8) 光程差 ↔ 延迟时间（含折射率）
# =========================================================
elif mode == "光程差 ↔ 延迟时间":
    st.subheader("✅ 光程差与延迟时间转换（考虑介质折射率）")

    submode = st.radio("转换方向：", ["延迟时间 → 物理长度差", "物理长度差 → 延迟时间"], horizontal=True)

    n = st.number_input("介质折射率 n（空气可近似 1.000）", min_value=1.0, value=1.0, step=0.001, format="%.6f")
    st.caption("这里默认群折射率≈相折射率，做工程估算；超快脉冲严格应用群折射率 n_g。")

    if submode == "延迟时间 → 物理长度差":
        c1, c2 = st.columns(2)
        with c1:
            t_val = st.number_input("延迟时间 Δt", min_value=0.0, value=1.0, step=0.1)
            t_unit = st.selectbox("Δt 单位", ["s", "ms", "us", "ns", "ps", "fs"], index=4)
        with c2:
            geom = st.radio("几何结构：", ["单程（一次通过）", "双程（反射往返）"], horizontal=True)

        dt = to_si(t_val, t_unit)
        if geom == "单程（一次通过）":
            dL = C0 * dt / n
        else:
            dL = C0 * dt / (2*n)

        st.success(f"对应物理长度差 ΔL ≈ {format_eng(dL, 'm')}")

    else:
        c1, c2 = st.columns(2)
        with c1:
            L_val = st.number_input("物理长度差 ΔL", min_value=0.0, value=0.300, step=0.001, format="%.6f")
            L_unit = st.selectbox("ΔL 单位", ["m", "mm", "um", "nm"], index=0)
        with c2:
            geom = st.radio("几何结构：", ["单程（一次通过）", "双程（反射往返）"], horizontal=True)

        dL = to_si(L_val, L_unit)
        if geom == "单程（一次通过）":
            dt = n * dL / C0
        else:
            dt = 2*n * dL / C0

        st.success(f"对应延迟时间 Δt ≈ {format_eng(dt, 's')}")

    st.markdown("---")
    st.markdown("### 计算公式与原理说明")
    st.latex(r"v=\frac{c}{n}")
    st.latex(r"\Delta t=\frac{n\,\Delta L}{c}\quad(\text{单程})")
    st.latex(r"\Delta t=\frac{2n\,\Delta L}{c}\quad(\text{双程往返})")
    st.markdown(
        "- 光在折射率为 $n$ 的介质中传播速度 $v=c/n$。\n"
        "- 单程通过长度差 $\\Delta L$ 产生的延迟为 $\\Delta t = \\Delta L / v = n\\Delta L/c$。\n"
        "- 若是反射镜往返结构，光程差加倍，因此延迟也加倍。\n"
        "- 超快脉冲严格应使用群折射率 $n_g$ 来计算群延迟；此处用于工程快速估算。"
    )

# =========================================================
# 9) 高斯光束发散角（波长 + 束腰）
# =========================================================
else:
    st.subheader("✅ 高斯光束发散角估算")

    st.write("由束腰半径 \(w_0\) 与波长 \(\lambda\) 估算远场发散角。")
    st.caption("默认理想 TEM00（M²=1）；若非理想可用 M² 修正。")

    c1, c2, c3 = st.columns(3)
    with c1:
        lam_val = st.number_input("波长 λ", min_value=0.0, value=1030.0, step=10.0)
        lam_unit = st.selectbox("λ 单位", ["nm", "um", "mm", "m"], index=0, key="div_lamu")
    with c2:
        w0_val = st.number_input("束腰半径 w0（1/e²）", min_value=0.0, value=5.0, step=0.5)
        w0_unit = st.selectbox("w0 单位", ["um", "mm", "m", "nm"], index=0, key="div_w0u")
    with c3:
        M2 = st.number_input("光束质量 M²（理想=1）", min_value=1.0, value=1.0, step=0.1, format="%.3f")

    lam = to_si(lam_val, lam_unit)
    w0 = to_si(w0_val, w0_unit)

    out_unit = st.selectbox("输出单位", ["mrad（半角）", "deg（半角）", "mrad（全角）", "deg（全角）"], index=0)

    if lam <= 0 or w0 <= 0:
        st.error("λ 与 w0 必须 > 0。")
    else:
        # 理想高斯远场半角发散：theta = λ/(π w0)；含M²修正：theta = M² λ/(π w0)
        theta_half = (M2 * lam) / (np.pi * w0)  # rad
        theta_full = 2 * theta_half

        if out_unit == "mrad（半角）":
            st.success(f"发散角 θ（半角）≈ {theta_half*1e3:.6g} mrad")
        elif out_unit == "deg（半角）":
            st.success(f"发散角 θ（半角）≈ {np.rad2deg(theta_half):.6g}°")
        elif out_unit == "mrad（全角）":
            st.success(f"发散角 2θ（全角）≈ {theta_full*1e3:.6g} mrad")
        else:
            st.success(f"发散角 2θ（全角）≈ {np.rad2deg(theta_full):.6g}°")

    st.markdown("---")
    st.markdown("### 计算公式与原理说明")
    st.latex(r"\theta_{\mathrm{half}}\approx \frac{\lambda}{\pi w_0}\quad(\text{理想高斯},\ M^2=1)")
    st.latex(r"\theta_{\mathrm{half}}\approx \frac{M^2\lambda}{\pi w_0}\quad(\text{非理想光束近似修正})")
    st.latex(r"\theta_{\mathrm{full}}=2\theta_{\mathrm{half}}")
    st.markdown(
        "- 高斯光束在远场的角分布与束腰大小互为傅里叶对应：束腰越小，发散越大。\n"
        "- 理想 TEM$_{00}$ 的半角发散近似为 $\\lambda/(\\pi w_0)$。\n"
        "- 实际光束可用 $M^2$ 放大发散角：$\\theta \\propto M^2$。"
    )
