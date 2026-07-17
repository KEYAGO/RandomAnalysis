import random
import sympy as sp
import numpy as np

# Son üretilen 15 fonksiyonu hafızada tutarak tekrarını kesinlikle engelliyoruz
_history = []
MAX_HISTORY = 15

def generate_random_expression():
    """Çok daha geniş katsayılar ve yepyeni matematiksel kalıplarla sonsuz varyasyon üretir."""
    x = sp.Symbol('x')
    
    # Çok daha zengin fonksiyon tipleri
    types = [
        "quadratic", "cubic", "quartic", 
        "trig_simple", "trig_double", "trig_product",
        "rational_bell", "rational_asymmetric", 
        "exponential", "gaussian_bell", "logarithmic"
    ]
    chosen_type = random.choice(types)
    
    # Sıfır hariç rastgele geniş katsayı üreteci
    def rc(low=-12, high=12):
        val = 0
        while val == 0:
            val = random.randint(low, high)
        return val

    if chosen_type == "quadratic":
        # ax^2 + bx + c
        expr = 0.5 * rc(-6, 6) * x**2 + rc(-5, 5) * x + rc(-10, 10)
        x_range = (-10.0, 10.0)
        y_range = (-30.0, 70.0)

    elif chosen_type == "cubic":
        # ax^3 + bx
        expr = 0.05 * rc(-4, 4) * x**3 - rc(-6, 6) * x
        x_range = (-6.0, 6.0)
        y_range = (-25.0, 25.0)

    elif chosen_type == "quartic":
        # ax^4 + bx^2 (W veya M eğrisi)
        expr = 0.005 * rc(-3, 3) * x**4 - 0.2 * rc(-4, 4) * x**2
        x_range = (-7.0, 7.0)
        y_range = (-20.0, 40.0)

    elif chosen_type == "trig_simple":
        # a * sin(b*x)
        a = rc(-10, 10)
        b = random.choice([0.3, 0.5, 1.0])
        expr = a * sp.sin(b * x)
        x_range = (-10.0, 10.0)
        y_range = (-float(abs(a) + 2), float(abs(a) + 2))

    elif chosen_type == "trig_double":
        # a * sin(bx) + c * cos(dx) (Karışık dalga)
        expr = rc(-6, 6) * sp.sin(0.4 * x) + rc(-4, 4) * sp.cos(0.2 * x)
        x_range = (-12.0, 12.0)
        y_range = (-12.0, 12.0)

    elif chosen_type == "trig_product":
        # Genliği büyüyen dalga: a * x * sin(bx)
        expr = 0.3 * rc(-4, 4) * x * sp.cos(0.5 * x)
        x_range = (-10.0, 10.0)
        y_range = (-12.0, 12.0)

    elif chosen_type == "rational_bell":
        # a / (b * x^2 + c)
        a = rc(-25, 25)
        expr = a / (0.1 * x**2 + random.choice([2, 3, 4]))
        x_range = (-8.0, 8.0)
        y_range = (-15.0, 15.0)

    elif chosen_type == "rational_asymmetric":
        # ax / (x^2 + b)
        expr = rc(-30, 30) * x / (x**2 + random.choice([3, 5, 8]))
        x_range = (-10.0, 10.0)
        y_range = (-8.0, 8.0)

    elif chosen_type == "exponential":
        # e^(ax) + b
        a = random.choice([-0.4, -0.2, 0.2, 0.4])
        b = rc(-15, 15)
        expr = 2 * sp.exp(a * x) + b
        x_range = (-5.0, 5.0)
        y_range = (float(b - 5), float(b + 25))

    elif chosen_type == "gaussian_bell":
        # Çan eğrisi: a * e^(-b * x^2)
        a = rc(-15, 15)
        expr = a * sp.exp(-0.15 * x**2)
        x_range = (-6.0, 6.0)
        y_range = (-10.0, 10.0)

    else: # logarithmic
        # a * ln(x^2 + b) + c
        a = rc(-5, 5)
        b = random.choice([2, 4, 6])
        c = rc(-10, 10)
        expr = a * sp.log(x**2 + b) + c
        x_range = (-8.0, 8.0)
        y_range = (-20.0, 30.0)

    return expr, x_range, y_range

def get_random_function():
    global _history
    
    # Hafızayı kontrol ederek tamamen benzersiz yeni bir fonksiyon seçiyoruz
    while True:
        f_expr, x_range, y_range = generate_random_expression()
        expr_str = str(f_expr)
        
        if expr_str not in _history:
            _history.append(expr_str)
            if len(_history) > MAX_HISTORY:
                _history.pop(0) # En eski fonksiyonu hafızadan siliyoruz
            break
            
    x_min, x_max = x_range
    y_min, y_max = y_range
    x = sp.Symbol('x')
    
    # Hızlı analitik türev hesapları
    df_expr = sp.diff(f_expr, x)
    ddf_expr = sp.diff(df_expr, x)
    
    x_vals = np.linspace(x_min, x_max, 200)
    
    f_lambdified = sp.lambdify(x, f_expr, modules=['numpy', 'math'])
    df_lambdified = sp.lambdify(x, df_expr, modules=['numpy', 'math'])
    ddf_lambdified = sp.lambdify(x, ddf_expr, modules=['numpy', 'math'])
    
    y_vals = np.vectorize(f_lambdified)(x_vals).tolist()
    y_prime_vals = np.vectorize(df_lambdified)(x_vals).tolist()
    y_double_prime_vals = np.vectorize(ddf_lambdified)(x_vals).tolist()
    
    # --- ANINDA SAYISAL NOKTA TESPİTİ ---
    roots = []
    extrema = []
    inflections = []
    
    try:
        y_int_val = float(f_expr.subs(x, 0).evalf())
        y_intercept = {"x": 0.0, "y": y_int_val, "label": f"y-int: (0, {y_int_val:.2f})"}
    except Exception:
        y_intercept = None

    for i in range(len(x_vals) - 1):
        x1, x2 = x_vals[i], x_vals[i+1]
        y1, y2 = y_vals[i], y_vals[i+1]
        yp1, yp2 = y_prime_vals[i], y_prime_vals[i+1]
        ypp1, ypp2 = y_double_prime_vals[i], y_double_prime_vals[i+1]
        
        if y1 * y2 < 0:
            rx = 0.5 * (x1 + x2)
            roots.append({"x": rx, "y": 0.0, "label": f"Root: ({rx:.2f}, 0)"})
            
        if yp1 * yp2 < 0:
            ex = 0.5 * (x1 + x2)
            try:
                ey = float(f_expr.subs(x, ex).evalf())
                test_val = float(ddf_expr.subs(x, ex).evalf())
                type_label = "Local Min" if test_val > 0 else "Local Max"
                extrema.append({"x": ex, "y": ey, "label": f"{type_label}: ({ex:.2f}, {ey:.2f})"})
            except Exception:
                pass
                
        if ypp1 * ypp2 < 0:
            ix = 0.5 * (x1 + x2)
            try:
                iy = float(f_expr.subs(x, ix).evalf())
                inflections.append({"x": ix, "y": iy, "label": f"Inflection: ({ix:.2f}, {iy:.2f})"})
            except Exception:
                pass

    return {
        "latex_f": sp.latex(f_expr),
        "latex_df": sp.latex(df_expr),
        "latex_ddf": sp.latex(ddf_expr),
        "x_data": x_vals.tolist(),
        "y_data": y_vals,
        "y_prime_data": y_prime_vals,
        "y_double_prime_data": y_double_prime_vals,
        "x_range": [x_min, x_max],
        "y_range": [y_min, y_max],
        "points": {
            "y_intercept": y_intercept,
            "roots": roots,
            "extrema": extrema,
            "inflections": inflections
        }
    }