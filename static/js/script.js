document.addEventListener("DOMContentLoaded", () => {
    const generateBtn = document.getElementById("generate-btn");
    const advancedBtn = document.getElementById("advanced-btn");
    const workspace = document.getElementById("workspace");
    const chartsWrapper = document.getElementById("charts-wrapper");
    const analysisPanel = document.getElementById("analysis-panel");
    const analysisContent = document.getElementById("analysis-content");

    const fxText = document.getElementById("fx-text");
    const dfxText = document.getElementById("dfx-text");
    const ddfxText = document.getElementById("ddfx-text");

    let currentData = null;
    let advancedMode = false;

    fetchAndRenderFunction();

    generateBtn.addEventListener("click", fetchAndRenderFunction);
    advancedBtn.addEventListener("click", toggleAdvancedMode);

    function toggleAdvancedMode() {
        advancedMode = !advancedMode;
        if (advancedMode) {
            advancedBtn.innerText = "Advanced View: ON";
            advancedBtn.classList.add("active");
            document.body.classList.add("scrollable"); // Body dikey kaydırılabilir olur
            chartsWrapper.className = "charts-list";
            analysisPanel.classList.remove("hidden");
        } else {
            advancedBtn.innerText = "Advanced View: OFF";
            advancedBtn.classList.remove("active");
            document.body.classList.remove("scrollable"); // Body tek ekrana kilitlenir
            chartsWrapper.className = "charts-grid";
            analysisPanel.classList.add("hidden");
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
        
        if (currentData) {
            renderPlots(currentData);
        }
    }

    function fetchAndRenderFunction() {
        generateBtn.disabled = true;
        generateBtn.innerText = "Calculating...";

        fetch("/generate")
            .then(response => {
                if (!response.ok) throw new Error("Server error.");
                return response.json();
            })
            .then(data => {
                currentData = data;
                fxText.innerHTML = `$$f(x) = ${data.latex_f}$$`;
                dfxText.innerHTML = `$$f'(x) = ${data.latex_df}$$`;
                ddfxText.innerHTML = `$$f''(x) = ${data.latex_ddf}$$`;

                if (window.MathJax) {
                    MathJax.typesetPromise();
                }

                renderPlots(data);
                generateAnalysisText(data);
            })
            .catch(error => {
                console.error("Error:", error);
                alert("Something went wrong. Please refresh.");
            })
            .finally(() => {
                generateBtn.disabled = false;
                generateBtn.innerText = "Generate Function";
            });
    }

    function renderPlots(data) {
        const xRange = data.x_range;
        const pts = data.points;

        // --- ORTAK Y-EKSENİ ARALIĞI HESAPLAMA ---
        // Üç veri kümesinin (f, f', f'') tüm y değerlerini birleştirerek sınırları belirliyoruz.
        const allYValues = [...data.y_data, ...data.y_prime_data, ...data.y_double_prime_data];
        
        let minY = Math.min(...allYValues);
        let maxY = Math.max(...allYValues);

        // Grafiklerin üstten/alttan sıfırlanıp kesilmemesi için ufak bir pay (%10) ekliyoruz.
        const margin = (maxY - minY) * 0.1 || 1.0;
        const commonYRange = [minY - margin, maxY + margin];

        let fxShapes = [];
        let dfxShapes = [];
        let ddfxShapes = [];
        
        const fxExtra = [];
        const dfxExtra = [];
        const ddfxExtra = [];

        // TÜM ANALİZ NOKTALARI VE HİZALAMA ÇİZGİLERİ SADECE ADVANCED MOD AÇIKKEN ÇİZİLİR
        if (advancedMode) {
            // --- DİKEY HİZALAMA ÇİZGİLERİ (SHAPES) ---
            if (pts.extrema) {
                pts.extrema.forEach(pt => {
                    const line = {
                        type: 'line',
                        x0: pt.x, y0: commonYRange[0] * 2, x1: pt.x, y1: commonYRange[1] * 2, // Ortak limite göre çizgileri uzatıyoruz
                        line: { color: '#f97316', width: 1.5, dash: 'dashdot' }
                    };
                    fxShapes.push(line);
                    dfxShapes.push(line);
                    ddfxShapes.push(line);
                });
            }

            if (pts.inflections) {
                pts.inflections.forEach(pt => {
                    const line = {
                        type: 'line',
                        x0: pt.x, y0: commonYRange[0] * 2, x1: pt.x, y1: commonYRange[1] * 2,
                        line: { color: '#10b981', width: 1.5, dash: 'dot' }
                    };
                    fxShapes.push(line);
                    dfxShapes.push(line);
                    ddfxShapes.push(line);
                });
            }

            // --- GRAFİKLERDEKİ NOKTALAR (TRACES) ---
            // 1. Ana f(x) Grafik Noktaları
            if (pts.roots) {
                fxExtra.push({
                    x: pts.roots.map(p => p.x), y: pts.roots.map(p => p.y),
                    mode: 'markers', name: 'Roots',
                    marker: { color: '#ef4444', size: 10, symbol: 'circle' },
                    text: pts.roots.map(p => p.label), hoverinfo: 'text'
                });
            }
            if (pts.y_intercept) {
                fxExtra.push({
                    x: [pts.y_intercept.x], y: [pts.y_intercept.y],
                    mode: 'markers', name: 'y-Intercept',
                    marker: { color: '#8b5cf6', size: 10, symbol: 'diamond' },
                    text: [pts.y_intercept.label], hoverinfo: 'text'
                });
            }
            if (pts.extrema) {
                fxExtra.push({
                    x: pts.extrema.map(p => p.x), y: pts.extrema.map(p => p.y),
                    mode: 'markers', name: 'Extrema',
                    marker: { color: '#f97316', size: 11, symbol: 'triangle-up' },
                    text: pts.extrema.map(p => p.label), hoverinfo: 'text'
                });
            }
            if (pts.inflections) {
                fxExtra.push({
                    x: pts.inflections.map(p => p.x), y: pts.inflections.map(p => p.y),
                    mode: 'markers', name: 'Inflections',
                    marker: { color: '#10b981', size: 10, symbol: 'square' },
                    text: pts.inflections.map(p => p.label), hoverinfo: 'text'
                });
            }

            // 2. Birinci Türev f'(x) Grafik Noktaları (f(x) ekstremumları x-eksenini keser)
            if (pts.extrema) {
                dfxExtra.push({
                    x: pts.extrema.map(p => p.x), y: pts.extrema.map(() => 0),
                    mode: 'markers', name: "f'(x) = 0",
                    marker: { color: '#f97316', size: 10, symbol: 'circle' },
                    text: pts.extrema.map(p => `Slope 0 Point at x = ${p.x.toFixed(2)}`), hoverinfo: 'text'
                });
            }
            if (pts.inflections) {
                dfxExtra.push({
                    x: pts.inflections.map(p => p.x), y: pts.inflections.map(p => {
                        const idx = data.x_data.reduce((prev, curr, i) => 
                            Math.abs(curr - p.x) < Math.abs(data.x_data[prev] - p.x) ? i : prev, 0);
                        return data.y_prime_data[idx];
                    }),
                    mode: 'markers', name: "Max Slope Point",
                    marker: { color: '#10b981', size: 10, symbol: 'triangle-up' },
                    text: pts.inflections.map(p => `Max/Min Slope Point at x = ${p.x.toFixed(2)}`), hoverinfo: 'text'
                });
            }

            // 3. İkinci Türev f''(x) Grafik Noktaları (f(x) büküm noktaları x-eksenini keser)
            if (pts.inflections) {
                ddfxExtra.push({
                    x: pts.inflections.map(p => p.x), y: pts.inflections.map(() => 0),
                    mode: 'markers', name: "f''(x) = 0",
                    marker: { color: '#10b981', size: 10, symbol: 'circle' },
                    text: pts.inflections.map(p => `Concavity Change (Root) at x = ${p.x.toFixed(2)}`), hoverinfo: 'text'
                });
            }
        }

        // Tüm grafikler (f, f', f'') artık aynı dinamik olarak hesaplanan commonYRange aralığını kullanıyor.
        drawChart("chart-fx", data.x_data, data.y_data, "f(x) Graph", "#1f77b4", xRange, commonYRange, fxExtra, fxShapes);
        drawChart("chart-dfx", data.x_data, data.y_prime_data, "f'(x) Graph", "#ff7f0e", xRange, commonYRange, dfxExtra, dfxShapes);
        drawChart("chart-ddfx", data.x_data, data.y_double_prime_data, "f''(x) Graph", "#2ca02c", xRange, commonYRange, ddfxExtra, ddfxShapes);
    }

    function generateAnalysisText(data) {
        const pts = data.points;
        const metrics = data.advanced_metrics || {};
        let html = "";

        // --- I. TEMEL & GEOMETRİK ÖZELLİKLER ---
        html += `
            <div class="analysis-item" style="border-left-color: #3b82f6;">
                <strong>Symmetry & Structure</strong><br>
                • <strong>Domain:</strong> ${metrics.domain || "R"}<br>
                • <strong>Range:</strong> ${metrics.range || "N/A"}<br>
                • <strong>Symmetry:</strong> ${metrics.symmetry || "None"}<br>
                • <strong>Boundedness:</strong> ${metrics.boundedness || "Analyzed range bounded"}<br>
                • <strong>Y-Intercept:</strong> ${pts.y_intercept ? `(0, ${pts.y_intercept.y.toFixed(2)})` : "None"}
            </div>
        `;

        // --- II. LİMİT & ASİMPTOTİK DAVRANIŞ ---
        const asymptotesText = Array.isArray(metrics.horizontal_asymptotes) 
            ? metrics.horizontal_asymptotes.join(", ") 
            : "None";
            
        html += `
            <div class="analysis-item" style="border-left-color: #ec4899;">
                <strong>Limits & Asymptotes</strong><br>
                • <strong>Limit as x → +∞:</strong> ${metrics.limit_inf || "N/A"}<br>
                • <strong>Limit as x → -∞:</strong> ${metrics.limit_neg_inf || "N/A"}<br>
                • <strong>Horizontal Asymptotes:</strong> ${asymptotesText}<br>
                • <strong>Monotonicity:</strong> ${metrics.monotonicity || "Changes over interval"}<br>
                • <strong>Concavity Profile:</strong> ${metrics.concavity || "Varies"}
            </div>
        `;

        // --- III. İNTEGRAL & ORTALAMA DEĞER ---
        html += `
            <div class="analysis-item" style="border-left-color: #eab308;">
                <strong>Integration & Area Analysis</strong><br>
                • <strong>Interval:</strong> ${metrics.integration_interval || "[-25, 25]"}<br>
                • <strong>Net Integral Value:</strong> ${metrics.integral_value || "Calculating..."}<br>
                • <strong>Average Function Value:</strong> ${metrics.average_value || "Calculating..."}<br>
                <span style="font-size: 0.75rem; color:#64748b;">*Integral represents the net area under the curve.</span>
            </div>
        `;

        // --- IV. KRİTİK NOKTALAR VE BÜKÜMLER ---
        if (pts.extrema && pts.extrema.length > 0) {
            pts.extrema.forEach(pt => {
                html += `
                    <div class="analysis-item extrema">
                        <strong>Extremum at x = ${pt.x.toFixed(2)}</strong><br>
                        • <strong>f(x):</strong> Local peak/valley at y = ${pt.y.toFixed(2)}.<br>
                        • <strong>f'(x):</strong> First derivative equals exactly 0 (Flat slope).<br>
                        • <strong>Tangent behavior:</strong> Horizontal line.
                    </div>
                `;
            });
        }

        if (pts.inflections && pts.inflections.length > 0) {
            pts.inflections.forEach(pt => {
                html += `
                    <div class="analysis-item inflection">
                        <strong>Inflection Point at x = ${pt.x.toFixed(2)}</strong><br>
                        • <strong>f(x):</strong> Point of concavity change.<br>
                        • <strong>f''(x):</strong> Second derivative crosses zero (Root).<br>
                        • <strong>Concavity shift:</strong> Tangent line cuts through the curve.
                    </div>
                `;
            });
        }

        if (pts.roots && pts.roots.length > 0) {
            html += `
                <div class="analysis-item root">
                    <strong>Function Roots (x-intercepts):</strong><br>
                    The points where the function graph crosses the horizontal line (y = 0):<br>
                    ${pts.roots.map(r => `• <strong>x = ${r.x.toFixed(2)}</strong> (Real Root)`).join("<br>")}
                </div>
            `;
        }

        if (!html) {
            html = "<p>No critical analytical points detected in this specific range view.</p>";
        }

        analysisContent.innerHTML = html;
    }

    function drawChart(divId, x, y, title, color, xRange, yRange, extraTraces = [], shapes = []) {
        const trace = {
            x: x, y: y,
            type: 'scatter', mode: 'lines',
            line: { color: color, width: 3 },
            name: title, hoverinfo: 'x+y'
        };

        const dataToPlot = [trace, ...extraTraces];

        const layout = {
            margin: { t: 30, b: 25, l: 35, r: 15 },
            hovermode: 'closest',
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            showlegend: (extraTraces.length > 0),
            legend: { x: 0, y: 1, font: { size: 9 }, bgcolor: 'rgba(255,255,255,0.7)' },
            xaxis: { range: xRange, gridcolor: '#e2e8f0', zerolinecolor: '#94a3b8', fixedrange: true },
            yaxis: { range: yRange, gridcolor: '#e2e8f0', zerolinecolor: '#94a3b8', fixedrange: true },
            shapes: shapes
        };

        const config = {
            responsive: true,
            displayModeBar: false
        };

        Plotly.newPlot(divId, dataToPlot, layout, config);
    }
});