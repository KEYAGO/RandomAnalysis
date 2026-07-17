import random
import sympy as sp
import numpy as np
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

x = sp.Symbol('x', real=True)

generated_history = []

def generate_random_expression():
    """Rastgele matematiksel ifadeler üreten motor."""
    templates_list = [
        # Trigonometrik kombinasyonlar
        lambda: random.randint(2, 6) * sp.sin(random.choice([0.5, 1, 2]) * x) + random.randint(-5, 5),
        lambda: random.randint(2, 6) * sp.cos(random.choice([0.5, 1, 2]) * x) + random.randint(-5, 5),
        # Polinomlar (2. ve 3. derece)
        lambda: random.randint(1, 3) * x**2 + random.randint(-6, 6) * x + random.randint(-8, 8),
        lambda: random.choice([-1, 1]) * 0.5 * x**3 + random.randint(-4, 4) * x,
        # Logaritmik ve Üstel kombinasyonlar
        lambda: random.randint(2, 6) * sp.log(x**2 + random.randint(1, 4)) - random.randint(2, 8),
        lambda: random.randint(1, 3) * sp.exp(random.choice([-0.1, -0.2]) * x) * sp.sin(2 * x)
    ]
    
    attempts = 0
    while attempts < 50:
        expr = random.choice(templates_list)()
        expr_str = str(expr)
        if expr_str not in generated_history:
            generated_history.append(expr_str)
            if len(generated_history) > 15:
                generated_history.pop(0)
            return expr
        attempts += 1
    return random.choice(templates_list)()

def find_numerical_sign_changes(x_vals, y_vals):
    """Sayısal olarak işaret değişimlerini yakalayan güvenli motor."""
    if not isinstance(y_vals, (list, np.ndarray)):
        return []
        
    detected_xs = []
    for i in range(len(x_vals) - 1):
        if y_vals[i] * y_vals[i+1] <= 0:
            divisor = (y_vals[i+1] - y_vals[i])
            x_approx = x_vals[i] - y_vals[i] * (x_vals[i+1] - x_vals[i]) / (divisor if divisor != 0 else 1)
            if not any(abs(x_approx - prev_x) < 0.2 for prev_x in detected_xs):
                detected_xs.append(float(x_approx))
    return detected_xs

def evaluate_symbolic_expression(expr, x_symbol, x_array):
    """Sembolik bir ifadeyi güvenli bir şekilde sayısal numpy dizisine dönüştürür."""
    f_num = sp.lambdify(x_symbol, expr, "numpy")
    try:
        res = f_num(x_array)
        if isinstance(res, (int, float, np.number)):
            res = np.full_like(x_array, res)
        return np.nan_to_num(res).tolist()
    except Exception:
        return np.zeros_like(x_array).tolist()

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/generate")
def generate_function():
    f = generate_random_expression()
    df = sp.diff(f, x)
    ddf = sp.diff(df, x)

    # İstediğin [-25, 25] simetrik aralığına güncellendi
    x_min, x_max = -25.0, 25.0
    x_vals = np.linspace(x_min, x_max, 600)
    
    y_vals = evaluate_symbolic_expression(f, x, x_vals)
    y_prime_vals = evaluate_symbolic_expression(df, x, x_vals)
    y_double_prime_vals = evaluate_symbolic_expression(ddf, x, x_vals)

    # --- DİNAMİK ANALİTİK NOKTA TESPİTİ ---
    root_xs = find_numerical_sign_changes(x_vals, y_vals)
    roots = [{"x": rx, "y": 0.0, "label": f"Root: x ≈ {rx:.2f}"} for rx in root_xs]
    
    try:
        y_int_val = float(f.subs(x, 0).evalf())
        y_intercept = {"x": 0.0, "y": y_int_val, "label": f"y-Intercept: (0, {y_int_val:.2f})"}
    except Exception:
        y_intercept = None

    extremum_xs = find_numerical_sign_changes(x_vals, y_prime_vals)
    extrema = []
    for ex in extremum_xs:
        try:
            ey = float(f.subs(x, ex).evalf())
            extrema.append({"x": ex, "y": ey, "label": f"Extremum: ({ex:.2f}, {ey:.2f})"})
        except Exception:
            pass

    inflection_xs = find_numerical_sign_changes(x_vals, y_double_prime_vals)
    inflections = []
    for ix in inflection_xs:
        try:
            iy = float(f.subs(x, ix).evalf())
            inflections.append({"x": ix, "y": iy, "label": f"Inflection: ({ix:.2f}, {iy:.2f})"})
        except Exception:
            pass

    points = {
        "roots": roots,
        "y_intercept": y_intercept,
        "extrema": extrema,
        "inflections": inflections
    }

    # --- AKADEMİK ANALİZ MOTORU ---
    
    # 1. Domain (Tanım Kümesi) & Range (Görüntü Kümesi) Analizi
    domain_str = "R (All Real Numbers)"
    try:
        # Sympy ile doğal tanım kümesini bulmayı deniyoruz
        domain_set = sp.continuous_domain(f, x, sp.S.Reals)
        if domain_set != sp.S.Reals:
            domain_str = sp.latex(domain_set)
    except Exception:
        pass

    # Sayısal Görüntü Kümesi (Range) Hesaplama
    min_y = min(y_vals)
    max_y = max(y_vals)
    range_str = f"[{min_y:.2f}, {max_y:.2f}]"

    # 2. Simetri Analizi
    symmetry = "None"
    try:
        if sp.simplify(f.subs(x, -x) - f) == 0:
            symmetry = "Even (Symmetric with respect to the y-axis)"
        elif sp.simplify(f.subs(x, -x) + f) == 0:
            symmetry = "Odd (Symmetric with respect to the origin)"
    except Exception:
        pass

    # 3. Sonsuz Limitleri ve Yatay Asimptotlar
    limit_inf = "Undefined"
    limit_neg_inf = "Undefined"
    horizontal_asymptotes = []
    
    try:
        lim_pos = sp.limit(f, x, sp.oo)
        limit_inf = str(lim_pos)
        if lim_pos.is_real:
            horizontal_asymptotes.append(f"y = {float(lim_pos):.2f}")
    except Exception:
        pass
        
    try:
        lim_neg = sp.limit(f, x, -sp.oo)
        limit_neg_inf = str(lim_neg)
        if lim_neg.is_real:
            horizontal_asymptotes.append(f"y = {float(lim_neg):.2f}")
    except Exception:
        pass

    # 4. Monotonicity (Artanlık / Azalanlık Durumu)
    monotonicity_status = "Changes over the interval"
    # Eğer tüm aralıkta türev >= 0 ise artan, <= 0 ise azalandır
    if all(yp >= -1e-5 for yp in y_prime_vals):
        monotonicity_status = "Strictly Increasing"
    elif all(yp <= 1e-5 for yp in y_prime_vals):
        monotonicity_status = "Strictly Decreasing"

    # 5. Concavity Profile (Konkavlık / Büküm Durumu)
    concavity_status = "Varies (Has inflection points)"
    if len(inflection_xs) == 0:
        if all(y_dp >= 0 for y_dp in y_double_prime_vals):
            concavity_status = "Concave Upwards (Convex)"
        elif all(y_dp <= 0 for y_dp in y_double_prime_vals):
            concavity_status = "Concave Downwards"

    # 6. Belirli İntegral ve Ortalama Değer
    integral_val_str = "Unable to integrate symbolically"
    avg_value_str = "N/A"
    try:
        exact_integral = sp.integrate(f, (x, x_min, x_max))
        if exact_integral.is_real:
            val = float(exact_integral.evalf())
            integral_val_str = f"{val:.4f}"
            avg_value_str = f"{(val / (x_max - x_min)):.4f}"
    except Exception:
        try:
            val = float(np.trapz(y_vals, x_vals))
            integral_val_str = f"{val:.4f} (Numerical Approx.)"
            avg_value_str = f"{(val / (x_max - x_min)):.4f}"
        except Exception:
            pass

    # 7. Sınırlılık Analizi
    boundedness = "Unbounded"
    try:
        lim_pos_inf = sp.limit(f, x, sp.oo)
        lim_neg_inf_val = sp.limit(f, x, -sp.oo)
        
        if lim_pos_inf.is_real and lim_neg_inf_val.is_real:
            boundedness = "Bounded (Both ends approach finite limits)"
        elif lim_pos_inf == sp.oo or lim_neg_inf_val == sp.oo:
            if lim_pos_inf != -sp.oo and lim_neg_inf_val != -sp.oo:
                boundedness = "Bounded from Below"
        elif lim_pos_inf == -sp.oo or lim_neg_inf_val == -sp.oo:
            if lim_pos_inf != sp.oo and lim_neg_inf_val != sp.oo:
                boundedness = "Bounded from Above"
    except Exception:
        pass

    return {
        "latex_f": sp.latex(f),
        "latex_df": sp.latex(df),
        "latex_ddf": sp.latex(ddf),
        "x_data": x_vals.tolist(),
        "y_data": y_vals,
        "y_prime_data": y_prime_vals,
        "y_double_prime_data": y_double_prime_vals,
        "x_range": [x_min, x_max],
        "y_range": [float(min(y_vals)) - 3, float(max(y_vals)) + 3],
        "points": points,
        "advanced_metrics": {
            "domain": domain_str,
            "range": range_str,
            "symmetry": symmetry,
            "limit_inf": limit_inf,
            "limit_neg_inf": limit_neg_inf,
            "horizontal_asymptotes": horizontal_asymptotes if horizontal_asymptotes else ["None"],
            "monotonicity": monotonicity_status,
            "concavity": concavity_status,
            "boundedness": boundedness,
            "integral_value": integral_val_str,
            "average_value": avg_value_str,
            "integration_interval": f"[{x_min}, {x_max}]"
        }
    }