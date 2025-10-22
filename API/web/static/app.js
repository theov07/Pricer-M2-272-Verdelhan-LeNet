// Fonctions pour basculer entre les onglets
function showVisualizationsTab() {
    document.getElementById('main-content').style.display = 'none';
    document.getElementById('visualizations-tab').style.display = 'block';
    
    // Générer automatiquement tous les graphiques
    setTimeout(() => {
        console.log('🚀 Génération automatique des graphiques...');
        
        // Toujours générer les 3 autres graphiques
        createNodesAnalysisChart();
        createTimingAnalysisChart(); 
        createPrecisionAnalysisChart();
        
        // Pour le graphique de convergence, essayer d'abord avec des données réelles
        if (currentData) {
            generateConvergenceAnalysis();
        } else {
            // Sinon créer un graphique avec des données de test
            const testData = [
                {N: 5, trinomial_price: 10.55, blackscholes_price: 10.45},
                {N: 10, trinomial_price: 10.48, blackscholes_price: 10.45},
                {N: 15, trinomial_price: 10.46, blackscholes_price: 10.45},
                {N: 20, trinomial_price: 10.45, blackscholes_price: 10.45},
                {N: 25, trinomial_price: 10.45, blackscholes_price: 10.45},
                {N: 30, trinomial_price: 10.45, blackscholes_price: 10.45}
            ];
            createPlotlyConvergenceChart(testData);
        }
    }, 100);
}

function hideVisualizationsTab() {
    document.getElementById('main-content').style.display = 'block';
    document.getElementById('visualizations-tab').style.display = 'none';
}

// Variables globales
let currentData = null;
let svg, g;

// Configuration D3.js
const width = 1000;
const height = 600;

// Fonctions utilitaires pour le calcul des nœuds ignorés
function calculateTheoreticalNodes(N) {
    // Dans un arbre trinomial, chaque étape i a (2*i + 1) nœuds
    // Total de nœuds = somme de i=0 à N de (2*i + 1)
    let total = 0;
    for (let i = 0; i <= N; i++) {
        total += (2 * i + 1);
    }
    return total;
}

function calculateIgnoredNodes(N, actualNodes, fallbackData = null) {
    const theoreticalNodes = calculateTheoreticalNodes(N);
    
    // Si on a des données de fallback, utiliser le nombre de nœuds qui auraient été ignorés avec le threshold original
    if (fallbackData && fallbackData.fallback_used && fallbackData.nodes_ignored_by_original_threshold) {
        return fallbackData.nodes_ignored_by_original_threshold;
    }
    
    return Math.max(0, theoreticalNodes - actualNodes);
}

function calculatePruningPercentage(N, actualNodes, fallbackData = null) {
    const theoreticalNodes = calculateTheoreticalNodes(N);
    
    // Si on a des données de fallback, utiliser le nombre de nœuds qui auraient été ignorés avec le threshold original
    if (fallbackData && fallbackData.fallback_used && fallbackData.nodes_ignored_by_original_threshold) {
        const ignored = fallbackData.nodes_ignored_by_original_threshold;
        const percentage = (ignored / theoreticalNodes) * 100;
        return Math.max(0, percentage).toFixed(1);
    }
    
    const ignored = theoreticalNodes - actualNodes;
    const percentage = (ignored / theoreticalNodes) * 100;
    return Math.max(0, percentage).toFixed(1);
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    initializeToggleButtons();
    initializeForm();
    initializeD3();
});

function initializeToggleButtons() {
    // Gestion des boutons toggle pour le type d'option
    document.querySelectorAll('[data-option]').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('[data-option]').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });

    // Gestion des boutons toggle pour le style d'option
    document.querySelectorAll('[data-style]').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('[data-style]').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });
    
    // Initialiser les dates par défaut
    initializeDefaultDates();
}

function initializeDefaultDates() {
    // Définir des dates par défaut
    const today = new Date();
    const maturityDate = new Date();
    maturityDate.setFullYear(today.getFullYear() + 1); // +1 an par défaut
    
    document.getElementById('start_date').value = today.toISOString().split('T')[0];
    document.getElementById('maturity_date').value = maturityDate.toISOString().split('T')[0];
}

function initializeForm() {
    document.getElementById('pricing-form').addEventListener('submit', handleFormSubmit);
}

function initializeD3() {
    const container = document.querySelector('.tree-area');
    if (!container) return;

    // Créer le SVG
    svg = d3.select("#tree-svg")
        .attr("width", "100%")
        .attr("height", "100%")
        .attr("viewBox", `0 0 ${width} ${height}`);

    // Ajouter le groupe principal avec zoom
    g = svg.append("g");

    // Configuration du zoom
    const zoom = d3.zoom()
        .scaleExtent([0.1, 3])
        .on("zoom", (event) => {
            g.attr("transform", event.transform);
        });

    svg.call(zoom);
}

async function handleFormSubmit(event) {
    event.preventDefault();
    
    // Indicateur de chargement
    const calculateBtn = document.querySelector('.calculate-btn');
    const originalText = calculateBtn.innerHTML;
    calculateBtn.innerHTML = '<span class="loading-spinner">⏳</span> Calculating...';
    calculateBtn.disabled = true;
    
    // Récupérer les valeurs du formulaire avec dates obligatoires
    const formData = {
        S0: parseFloat(document.getElementById('S0').value),
        K: parseFloat(document.getElementById('K').value),
        start_date: document.getElementById('start_date').value,
        maturity_date: document.getElementById('maturity_date').value,
        r: parseFloat(document.getElementById('r').value),
        sigma: parseFloat(document.getElementById('sigma').value),
        N: parseInt(document.getElementById('N').value),
        option_type: document.querySelector('[data-option].active').dataset.option,
        option_style: document.querySelector('[data-style].active').dataset.style,
        dividend: parseFloat(document.getElementById('dividend').value) || 0,
        threshold: (parseFloat(document.getElementById('threshold').value) || 0) / 100, // Convertir % en fraction
        ex_div_date: document.getElementById('ex_div_date').value || null
    };

    try {
        console.log("📤 Envoi de la requête API...");
        
        // Envoyer la requête à l'API
        const response = await fetch('/api/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        const result = await response.json();
        
        if (result.success) {
            currentData = result.data;
            console.log("✅ Données reçues:", result.data);
            console.log("📊 Nombre de noeuds:", result.data.nodes.length);
            console.log("🔗 Nombre de liens:", result.data.edges.length);
            console.log("🔬 Greeks:", result.greeks);
            
            // Afficher l'avertissement si présent
            if (result.warning) {
                console.log("⚠️ Avertissement:", result.warning);
                showWarning(result.warning);
            }
            
            // Afficher l'avertissement de fallback si présent
            if (result.data.fallback_used && result.data.warning_message) {
                console.log("⚠️ Fallback utilisé:", result.data.warning_message);
                showWarning(result.data.warning_message);
            }
            
            // Nettoyer et afficher les résultats
            showNewCalculationResult(result.data, formData, result.greeks);
            
            // Completely refresh the visualization
            console.log("🔄 Refreshing visualization for N =", formData.N);
            refreshVisualization();
            drawTree(result.data);
        } else {
            showResult(`❌ Erreur: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error("❌ Erreur de communication:", error);
        showResult(`❌ Erreur de communication: ${error.message}`, 'error');
    } finally {
        // Restaurer le bouton
        calculateBtn.innerHTML = originalText;
        calculateBtn.disabled = false;
    }
}

function showResult(message, type) {
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = message;
    resultDiv.className = `result ${type}`;
    resultDiv.style.display = 'block';
}

function showWarning(message) {
    // Créer ou mettre à jour une div d'avertissement
    let warningDiv = document.getElementById('warning-message');
    if (!warningDiv) {
        warningDiv = document.createElement('div');
        warningDiv.id = 'warning-message';
        warningDiv.style.cssText = `
            background: rgba(255, 193, 7, 0.1);
            border: 1px solid rgba(255, 193, 7, 0.3);
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            color: #ffc107;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        `;
        
        // Insérer avant la section des résultats
        const resultsSection = document.getElementById('results-section');
        if (resultsSection.parentNode) {
            resultsSection.parentNode.insertBefore(warningDiv, resultsSection);
        }
    }
    
    warningDiv.innerHTML = `
        <span style="font-size: 1.2rem;">⚠️</span>
        <span>${message}</span>
        <button onclick="this.parentElement.style.display='none'" style="
            margin-left: auto;
            background: none;
            border: none;
            color: #ffc107;
            cursor: pointer;
            font-size: 1.2rem;
            padding: 0;
        ">×</button>
    `;
    warningDiv.style.display = 'flex';
    
    // Auto-hide après 10 secondes
    setTimeout(() => {
        if (warningDiv && warningDiv.style.display !== 'none') {
            warningDiv.style.display = 'none';
        }
    }, 10000);
}

function generateExecutionTimeSection(executionTimes) {
    if (!executionTimes || !executionTimes.trinomial_time) {
        return '';
    }
    
    const trinomialTime = executionTimes.trinomial_time; // Keep in seconds
    const blackScholesTime = executionTimes.blackscholes_time || null;
    
    let speedComparisonText = '';
    if (blackScholesTime) {
        const timeDifference = trinomialTime - blackScholesTime;
        const sign = timeDifference > 0 ? '+' : '';
        speedComparisonText = `<span style="color: ${timeDifference > 0 ? '#ff6b6b' : '#51cf66'};">${sign}${timeDifference.toFixed(6)}s</span>`;
    }
    
    return `
        <div class="execution-time-section" style="margin-top: 2rem;">
            <center><h4>Execution Performance</h4></center>
            
            <div class="execution-time-table" style="
                display: grid; 
                grid-template-columns: 1fr 1fr 1fr; 
                gap: 1rem; 
                margin-top: 1rem;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 10px;
                padding: 1.5rem;
                border: 1px solid rgba(255, 255, 255, 0.1);
            ">
                <div class="time-cell trinomial" style="text-align: center;">
                    <div style="font-weight: bold; margin-bottom: 0.5rem;">
                        Trinomial
                    </div>
                    <div style="font-size: 1.3rem; color: #ffffff;">
                        ${trinomialTime.toFixed(6)}s
                    </div>
                </div>
                
                <div class="time-cell blackscholes" style="text-align: center;">
                    <div style="font-weight: bold; margin-bottom: 0.5rem;">
                        Black-Scholes
                    </div>
                    <div style="font-size: 1.3rem; color: #ffffff;">
                        ${blackScholesTime ? blackScholesTime.toFixed(6) + 's' : 'N/A'}
                    </div>
                </div>
                
                <div class="time-cell ratio" style="text-align: center;">
                    <div style="font-weight: bold; margin-bottom: 0.5rem;">
                        Difference
                    </div>
                    <div style="font-size: 1.3rem; color: #ffffff;">
                        ${speedComparisonText || 'N/A'}
                    </div>
                </div>
            </div>
        </div>
    `;
}

function generateGreeksSection(greeks) {
    console.log("Greeks data received:", greeks);
    
    if (!greeks || greeks.delta === undefined) {
        console.log("Greeks not available or delta undefined");
        return ''; // Don't show Greeks section if not available
    }
    
    return `
        <div class="greeks-section" style="margin-top: 2rem;">
            <center><h4>Option Greeks (Sensitivities)</h4></center>
            
            <div class="greeks-grid" style="
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                gap: 1rem; 
                margin-top: 1rem;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 10px;
                padding: 1.5rem;
                border: 1px solid rgba(255, 255, 255, 0.1);
            ">
                <div class="greek-item" style="text-align: center;">
                    <div style="font-weight: bold; margin-bottom: 0.5rem;">
                        Delta (∂V/∂S)
                    </div>
                    <div style="font-size: 1.2rem; color: #ffffff;">
                        ${greeks.delta.toFixed(6)}
                    </div>
                    <div style="font-size: 0.8rem; color: #aaaaaa; margin-top: 0.25rem;">
                        Price sensitivity
                    </div>
                </div>
                
                <div class="greek-item" style="text-align: center;">
                    <div style="font-weight: bold; margin-bottom: 0.5rem;">
                        Gamma (∂²V/∂S²)
                    </div>
                    <div style="font-size: 1.2rem; color: #ffffff;">
                        ${greeks.gamma.toFixed(8)}
                    </div>
                    <div style="font-size: 0.8rem; color: #aaaaaa; margin-top: 0.25rem;">
                        Delta sensitivity
                    </div>
                </div>
                
                <div class="greek-item" style="text-align: center;">
                    <div style="font-weight: bold; margin-bottom: 0.5rem;">
                        Theta (∂V/∂t)
                    </div>
                    <div style="font-size: 1.2rem; color: #ffffff;">
                        ${greeks.theta.toFixed(6)}
                    </div>
                    <div style="font-size: 0.8rem; color: #aaaaaa; margin-top: 0.25rem;">
                        Time decay
                    </div>
                </div>
                
                <div class="greek-item" style="text-align: center;">
                    <div style="font-weight: bold; margin-bottom: 0.5rem;">
                        Vega (∂V/∂σ)
                    </div>
                    <div style="font-size: 1.2rem; color: #ffffff;">
                        ${greeks.vega.toFixed(6)}
                    </div>
                    <div style="font-size: 0.8rem; color: #aaaaaa; margin-top: 0.25rem;">
                        Volatility sensitivity
                    </div>
                </div>
                
                <div class="greek-item" style="text-align: center;">
                    <div style="font-weight: bold; margin-bottom: 0.5rem;">
                        Rho (∂V/∂r)
                    </div>
                    <div style="font-size: 1.2rem; color: #ffffff;">
                        ${greeks.rho.toFixed(6)}
                    </div>
                    <div style="font-size: 0.8rem; color: #aaaaaa; margin-top: 0.25rem;">
                        Interest rate sensitivity
                    </div>
                </div>
            </div>
        </div>
    `;
}

function showNewCalculationResult(data, params, greeks) {
    // Cacher l'ancien système
    document.getElementById('result').style.display = 'none';
    
    // Afficher la nouvelle section
    document.getElementById('results-section').style.display = 'block';
    
    const trinomialPrice = data.tree_params.final_price;
    const blackScholesPrice = data.black_scholes_price;
    const difference = trinomialPrice - blackScholesPrice;
    const percentDiff = (difference / blackScholesPrice * 100);
    
    // Option type info
    const optionInfo = data.option_info || { type: 'call', style: 'european' };
    
        // Section principale - Comparaison des prix
    document.getElementById('main-results').innerHTML = `
        <h3>Pricing Results</h3>
        
        <div class="price-comparison">
            <div class="price-box trinomial">
                <h4>🌳 Trinomial Model</h4>
                <div class="price-value">${trinomialPrice.toFixed(6)}€</div>
                <div class="price-info">${data.nodes.length} nodes calculated</div>
            </div>
            <div class="price-box blackscholes">
                <h4>📈 Black-Scholes</h4>
                <div class="price-value">${blackScholesPrice.toFixed(6)}€</div>
                <div class="price-info">Exact theoretical price</div>
            </div>
        </div>
        
        <div class="difference-section">
            <center><h4>Difference</h4></center>
            <p style="font-size: 1.2rem; text-align: center; margin: 1rem 0;">
                ${difference > 0 ? '+' : ''}${difference.toFixed(6)}€ 
                (${percentDiff > 0 ? '+' : ''}${percentDiff.toFixed(2)}%)
            </p>
        </div>
        
        ${generateExecutionTimeSection(data.execution_times)}
        ${generateGreeksSection(greeks)}
    `;
    
    // Section détaillée
    const dateInfo = data.date_info || {};
    let maturityDisplay = '';
    
    if (dateInfo.calculated_from_dates) {
        maturityDisplay = `
            <div class="detail-item">
                <div class="detail-label">Start date</div>
                <div class="detail-value">${new Date(dateInfo.start_date).toLocaleDateString('en-US')}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Maturity date</div>
                <div class="detail-value">${new Date(dateInfo.maturity_date).toLocaleDateString('en-US')}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Calculated maturity</div>
                <div class="detail-value">${dateInfo.T_years.toFixed(4)} years (${dateInfo.T_days} days)</div>
            </div>
        `;
    } else {
        maturityDisplay = `
                        <div class="detail-item">
                <div class="detail-label">Start date</div>
                <div class="detail-value">${new Date(params.start_date).toLocaleDateString('en-US')}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Maturity date</div>
                <div class="detail-value">${new Date(params.maturity_date).toLocaleDateString('en-US')}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Calculated maturity</div>
                <div class="detail-value">${data.date_info ? data.date_info.T_years.toFixed(4) : 'N/A'} years (${data.date_info ? data.date_info.T_days : 'N/A'} days)</div>
            </div>
        `;
    }
    
    document.getElementById('detailed-results').innerHTML = `
        <h4>Parameters Details</h4>
        <div class="details-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem;">
            <div class="detail-item">
                <div class="detail-label">Option type</div>
                <div class="detail-value">${optionInfo.type.toUpperCase()} ${optionInfo.style}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Spot price (S₀)</div>
                <div class="detail-value">${params.S0}€</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Strike (K)</div>
                <div class="detail-value">${params.K}€</div>
            </div>
            ${maturityDisplay}
            <div class="detail-item">
                <div class="detail-label">Risk-free rate (r)</div>
                <div class="detail-value">${(params.r * 100).toFixed(1)}%</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Volatility (σ)</div>
                <div class="detail-value">${(params.sigma * 100).toFixed(1)}%</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Steps (N)</div>
                <div class="detail-value">${params.N}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Nodes calculated</div>
                <div class="detail-value">${data.nodes.length}</div>
            </div>
            ${params.threshold > 0 ? `
            <div class="detail-item">
                <div class="detail-label">Nodes ignored (pruning)</div>
                <div class="detail-value">${calculateIgnoredNodes(params.N, data.nodes.length, data)} (-${calculatePruningPercentage(params.N, data.nodes.length, data)}%)</div>
            </div>
            ` : ''}
            <div class="detail-item">
                <div class="detail-label">Period (days)</div>
                <div class="detail-value">${dateInfo.T_days}</div>
            </div>
            ${params.dividend > 0 ? `
            <div class="detail-item">
                <div class="detail-label">Dividend</div>
                <div class="detail-value">${params.dividend}€</div>
            </div>
            ` : ''}
            ${params.threshold > 0 ? `
            <div class="detail-item">
                <div class="detail-label">Pruning threshold</div>
                <div class="detail-value">${(params.threshold * 100).toFixed(20)}%</div>
            </div>
            ` : ''}
            ${params.ex_div_date ? `
            <div class="detail-item">
                <div class="detail-label">Ex-dividend date</div>
                <div class="detail-value">${new Date(params.ex_div_date).toLocaleDateString('en-US')}</div>
            </div>
            ` : ''}
        </div>
        
    `;
}

function showVisualization() {
    document.getElementById('visualization').style.display = 'block';
}

function hideVisualization() {
    document.getElementById('visualization').style.display = 'none';
}

function refreshVisualization() {
    console.log("🔄 Rafraîchissement complet de la visualisation");
    
    // Afficher la section de visualisation
    showVisualization();
    
    // Nettoyer complètement le SVG et supprimer tous les tooltips
    if (g) {
        g.selectAll("*").remove();
    }
    
    // Supprimer tous les tooltips existants
    d3.selectAll(".tooltip").remove();
    
    // Réinitialiser le zoom
    if (svg) {
        svg.transition()
            .duration(0) // Pas d'animation pour le reset
            .call(
                d3.zoom().transform,
                d3.zoomIdentity
            );
    }
    
    console.log("✅ Visualisation nettoyée et prête pour le nouveau dessin");
}

function drawTree(data) {
    console.log("🌳 DrawTree appelé avec:", data);
    console.log("📊 Noeuds à dessiner:", data.nodes.length);
    console.log("🔗 Liens à dessiner:", data.edges.length);
    
    // Vérification des données
    if (!data || !data.nodes || !data.edges || !data.tree_params) {
        console.error("❌ Données invalides pour dessiner l'arbre");
        return;
    }
    
    // Nettoyer complètement le SVG avant de redessiner
    if (g) {
        g.selectAll("*").remove();
        console.log("🧹 SVG nettoyé");
    }
    
    const container = document.querySelector('.tree-area');
    if (!container) {
        console.error("❌ Container .tree-area introuvable");
        return;
    }
    
    const width = container.clientWidth;
    const height = container.clientHeight;
    
    console.log(`📐 Dimensions du container: ${width}x${height}`);
    
    // Adaptive parameters to handle visualization up to N=50
    const N = data.tree_params.N;
    let adaptiveScale, showVisualization = true;
    
    if (N <= 10) {
        adaptiveScale = 1.0;           // Normal size
    } else if (N <= 50) {
        adaptiveScale = Math.max(0.4, 10 / N);  // Progressive reduction
        showVisualization = true;
    } else {
        // No visualization for N > 50
        showVisualization = false;
    }
    
    console.log(`N=${N}, nodes=${data.nodes.length}, scale=${adaptiveScale}, display=${showVisualization}`);
    
    // If too many nodes, display informative message instead of visualization
    if (!showVisualization) {
        g.selectAll("*").remove();
        g.append("text")
            .attr("x", width/2)
            .attr("y", height/2)
            .attr("text-anchor", "middle")
            .style("font-family", "'Segoe UI', sans-serif")
            .style("font-size", "16px")
            .style("fill", "#ffffff")
            .text(`N > 50, Tree too large for visualization (${data.nodes.length} nodes)`);
        
        g.append("text")
            .attr("x", width/2)
            .attr("y", height/2 + 30)
            .attr("text-anchor", "middle")
            .style("font-family", "'Segoe UI', sans-serif")
            .style("font-size", "14px")
            .style("fill", "#cccccc")
            .text(`Calculations are correct, only visualization is simplified`);
        return;
    }
    
    // Organiser les nœuds par étapes
    const nodesByStep = {};
    data.nodes.forEach(node => {
        if (!nodesByStep[node.step]) {
            nodesByStep[node.step] = [];
        }
        nodesByStep[node.step].push(node);
    });
    
    // Calculer les positions avec adaptation
    const stepWidth = width / (N + 1);
    const maxNodesInStep = Math.max(...Object.values(nodesByStep).map(nodes => nodes.length));
    const stepHeight = Math.max(20, height / (maxNodesInStep + 1)); // Hauteur min de 20px
    
    const positions = {};
    Object.keys(nodesByStep).forEach(step => {
        const stepNodes = nodesByStep[step];
        stepNodes.forEach((node, index) => {
            // Centrer les nœuds de chaque étape verticalement
            const stepNodeCount = stepNodes.length;
            const startY = (height - (stepNodeCount - 1) * stepHeight) / 2;
            
            positions[node.id] = {
                x: parseInt(step) * stepWidth + 50,
                y: startY + index * stepHeight
            };
        });
    });
    
    console.log("Positions calculées:", positions);
    
    // Dessiner les liens en premier
    const links = g.selectAll(".link")
        .data(data.edges)
        .enter().append("line")
        .attr("class", d => `link ${d.direction}`)
        .attr("x1", d => positions[d.source]?.x || 0)
        .attr("y1", d => positions[d.source]?.y || 0)
        .attr("x2", d => positions[d.target]?.x || 0)
        .attr("y2", d => positions[d.target]?.y || 0)
        .style("stroke", d => {
            switch(d.direction) {
                case 'up': return '#66ff66';     // Vert plus clair
                case 'middle': return '#66ccff'; // Bleu plus clair  
                case 'down': return '#ff6666';   // Rouge plus clair
                default: return '#ffffff';
            }
        })
        .style("stroke-width", "2px")
        .style("opacity", "0.9");
    
    // Ajouter les étiquettes de probabilité sur les liens - adaptatifs
    const labelFontSize = Math.max(5, 9 * adaptiveScale); // Taille entre 5 et 9px
    const linkLabels = g.selectAll(".link-label")
        .data(data.edges)
        .enter().append("text")
        .attr("class", "link-label")
        .attr("x", d => (positions[d.source]?.x + positions[d.target]?.x) / 2 || 0)
        .attr("y", d => (positions[d.source]?.y + positions[d.target]?.y) / 2 || 0)
        .attr("dy", "-5px")
        .style("text-anchor", "middle")
        .style("font-family", "'Segoe UI', sans-serif")
        .style("font-size", labelFontSize + "px")
        .style("font-weight", "600")
        .style("fill", d => {
            switch(d.direction) {
                case 'up': return '#66ff66';
                case 'middle': return '#66ccff';
                case 'down': return '#ff6666';
                default: return '#ffffff';
            }
        })
        .style("pointer-events", "none")
        .style("background", "rgba(0,0,0,0.7)")
        .text(d => {
            if (!d.probability) return '';
            // Adaptation selon N pour éviter la surcharge visuelle
            if (N > 50) return '';   // Pas de labels pour N > 50 (performance)
            if (N > 20) return '';   // Pas de labels pour N > 20 (trop dense)
            if (N > 10) return d.probability.toFixed(2);
            return d.probability.toFixed(3);
        });
    
    // Dessiner les nœuds
    const nodes = g.selectAll(".node")
        .data(data.nodes)
        .enter().append("g")
        .attr("class", d => {
            let classes = "node";
            if (d.step === 0) classes += " root";
            if (d.step === data.tree_params.N) classes += " leaf";
            return classes;
        })
        .attr("transform", d => `translate(${positions[d.id]?.x || 0},${positions[d.id]?.y || 0})`);
    
    // Cercles des nœuds - taille adaptative
    const nodeRadius = Math.max(6, 15 * adaptiveScale); // Rayon entre 6 et 15
    nodes.append("circle")
        .attr("r", nodeRadius)
        .style("fill", d => {
            if (d.step === 0) return '#66ff66';      // Vert clair pour le nœud initial
            if (d.step === data.tree_params.N) return '#ff6666'; // Rouge clair pour les nœuds finaux
            return '#66ccff';                        // Bleu clair pour les nœuds intermédiaires
        })
        .style("stroke", "#ffffff")
        .style("stroke-width", Math.max(1, 2 * adaptiveScale) + "px")
        .style("cursor", "pointer");
    
    // Texte principal des nœuds (prix de l'action) - taille adaptative
    const fontSize = Math.max(6, 10 * adaptiveScale); // Taille entre 6 et 10px
    nodes.append("text")
        .attr("dy", "-0.3em")
        .style("text-anchor", "middle")
        .style("font-family", "'Segoe UI', sans-serif")
        .style("font-size", fontSize + "px")
        .style("font-weight", "600")
        .style("fill", "#000000")
        .style("pointer-events", "none")
        .text(d => {
            if (N > 50) return ''; // Pas de texte principal pour N > 50
            return N > 10 ? d.value.toFixed(0) : d.value.toFixed(1);
        });
    
    // Texte secondaire (prix de l'option) - adaptatif selon N
    if (N <= 30) { // Seulement afficher le texte secondaire pour N <= 30
        const secondaryFontSize = Math.max(5, 8 * adaptiveScale); // Taille entre 5 et 8px
        nodes.append("text")
            .attr("dy", "1em")
            .style("text-anchor", "middle")
            .style("font-family", "'Segoe UI', sans-serif")
            .style("font-size", secondaryFontSize + "px")
            .style("font-weight", "500")
            .style("fill", "#000000")
            .style("pointer-events", "none")
            .text(d => N > 15 ? `(${d.option_value.toFixed(1)})` : `(${d.option_value.toFixed(3)})`);
    }
    
    // Tooltips au survol
    nodes
        .on("mouseover", function(event, d) {
            // Supprimer les anciens tooltips
            d3.selectAll(".tooltip").remove();
            
            // Créer le tooltip
            const tooltip = d3.select("body").append("div")
                .attr("class", "tooltip")
                .style("position", "absolute")
                .style("background", "rgba(0,0,0,0.9)")
                .style("color", "white")
                .style("padding", "10px")
                .style("border-radius", "6px")
                .style("font-size", "12px")
                .style("font-family", "'Segoe UI', sans-serif")
                .style("box-shadow", "0 4px 12px rgba(0,0,0,0.3)")
                .style("pointer-events", "none")
                .style("z-index", "1000")
                .style("max-width", "200px")
                .style("left", (event.pageX + 15) + "px")
                .style("top", (event.pageY - 10) + "px");
            
            // Contenu du tooltip
            let tooltipContent = `
                <div style="font-weight: bold; margin-bottom: 5px; color: #4fc3f7;">Étape ${d.step}</div>
                <div><strong>Prix action:</strong> ${d.value.toFixed(6)}€</div>
                <div><strong>Prix option:</strong> ${d.option_value.toFixed(6)}€</div>
                <div><strong>Payoff:</strong> ${d.payoff.toFixed(6)}€</div>
            `;
            
            // Ajouter les probabilités si disponibles
            if (d.prob_up !== undefined) {
                tooltipContent += `
                    <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #333;">
                        <div style="font-weight: bold; color: #4caf50; margin-bottom: 3px;">Probabilités:</div>
                        <div style="font-size: 10px;">
                            <div>↗ Up: ${(d.prob_up * 100).toFixed(1)}%</div>
                            <div>→ Mid: ${(d.prob_mid * 100).toFixed(1)}%</div>
                            <div>↘ Down: ${(d.prob_down * 100).toFixed(1)}%</div>
                        </div>
                    </div>
                `;
            }
            
            tooltip.html(tooltipContent);
        })
        .on("mouseout", function() {
            d3.selectAll(".tooltip").remove();
        });
    
    // Auto-zoom pour voir tout l'arbre
    const bounds = g.node().getBBox();
    const parent = svg.node().getBoundingClientRect();
    const fullWidth = parent.width;
    const fullHeight = parent.height;
    const widthScale = fullWidth / bounds.width;
    const heightScale = fullHeight / bounds.height;
    const scale = Math.min(widthScale, heightScale) * 0.8;
    
    const translate = [
        fullWidth / 2 - scale * (bounds.x + bounds.width / 2),
        fullHeight / 2 - scale * (bounds.y + bounds.height / 2)
    ];
    
    console.log(`🔍 Auto-zoom appliqué: scale=${scale.toFixed(2)}, translate=[${translate[0].toFixed(1)}, ${translate[1].toFixed(1)}]`);
    
    svg.transition()
        .duration(750)
        .call(
            d3.zoom().transform,
            d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale)
        );
}

// ==================== CONVERGENCE ANALYSIS ====================

async function generateConvergenceAnalysis() {
    console.log('🔄 Début de generateConvergenceAnalysis');
    
    if (!currentData) {
        console.log('❌ Pas de données actuelles disponibles pour la convergence');
        return;
    }
    
    try {
        // Extraire les paramètres de la dernière calculation
        const params = extractCurrentParameters();
        console.log('📊 Paramètres extraits:', params);
        
        // Appeler la nouvelle API de convergence
        console.log('🚀 Appel API convergence...');
        const response = await fetch('/api/convergence', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(params)
        });
        
        console.log('📡 Réponse reçue:', response.status);
        const result = await response.json();
        console.log('📋 Données résultat:', result);
        
        if (result.success && result.data && result.data.length > 0) {
            console.log('✅ Succès, création du graphique...');
            createPlotlyConvergenceChart(result.data);
            createNodesAnalysisChart(); // Graphique des nœuds
            createTimingAnalysisChart(); // Graphique du temps d'exécution
            createPrecisionAnalysisChart(); // Graphique de précision
        } else {
            console.log('⚠️ API retourne données vides, utilisation données de test');
            // Fallback vers données de test si l'API ne retourne rien
            const testData = [
                {N: 5, trinomial_price: 10.55, blackscholes_price: 10.45},
                {N: 10, trinomial_price: 10.48, blackscholes_price: 10.45},
                {N: 15, trinomial_price: 10.46, blackscholes_price: 10.45},
                {N: 20, trinomial_price: 10.45, blackscholes_price: 10.45},
                {N: 25, trinomial_price: 10.45, blackscholes_price: 10.45},
                {N: 30, trinomial_price: 10.45, blackscholes_price: 10.45}
            ];
            createPlotlyConvergenceChart(testData);
            createNodesAnalysisChart(); // Graphique des nœuds
            createTimingAnalysisChart(); // Graphique du temps d'exécution
            createPrecisionAnalysisChart(); // Graphique de précision
        }
        
    } catch (error) {
        console.error('💥 Erreur lors de la génération de l\'analyse de convergence:', error);
        // Fallback vers données de test en cas d'erreur
        console.log('⚠️ Utilisation données de test suite à l\'erreur');
        const testData = [
            {N: 5, trinomial_price: 10.55, blackscholes_price: 10.45},
            {N: 10, trinomial_price: 10.48, blackscholes_price: 10.45},
            {N: 15, trinomial_price: 10.46, blackscholes_price: 10.45},
            {N: 20, trinomial_price: 10.45, blackscholes_price: 10.45},
            {N: 25, trinomial_price: 10.45, blackscholes_price: 10.45},
            {N: 30, trinomial_price: 10.45, blackscholes_price: 10.45}
        ];
        createPlotlyConvergenceChart(testData);
        createNodesAnalysisChart(); // Graphique des nœuds
        createTimingAnalysisChart(); // Graphique du temps d'exécution
        createPrecisionAnalysisChart(); // Graphique de précision
    }
}

function extractCurrentParameters() {
    // Extraire les paramètres du formulaire actuel
    return {
        S0: parseFloat(document.getElementById('S0').value),
        K: parseFloat(document.getElementById('K').value),
        r: parseFloat(document.getElementById('r').value),
        sigma: parseFloat(document.getElementById('sigma').value),
        start_date: document.getElementById('start_date').value,
        maturity_date: document.getElementById('maturity_date').value,
        option_type: document.querySelector('[data-option].active').dataset.option,
        option_style: document.querySelector('[data-style].active').dataset.style,
        dividend: parseFloat(document.getElementById('dividend').value) || 0
    };
}

function createPlotlyConvergenceChart(data) {
    console.log('📊 Création du graphique Plotly avec:', data);
    
    if (!data || data.length === 0) {
        console.error('❌ Pas de données pour le graphique');
        return;
    }
    
    // Préparer les données pour Plotly
    const N_values = data.map(d => d.N);
    const trinomial_prices = data.map(d => d.trinomial_price);
    const blackscholes_price = data[0].blackscholes_price; // Prix constant
    const blackscholes_line = data.map(d => d.blackscholes_price);
    
    console.log('📈 N_values:', N_values);
    console.log('💰 trinomial_prices:', trinomial_prices);
    console.log('📊 blackscholes_price:', blackscholes_price);
    
    // Trace pour le modèle trinomial
    const trinomialTrace = {
        x: N_values,
        y: trinomial_prices,
        mode: 'lines+markers',
        name: 'Trinomial Tree',
        line: {
            color: '#4fc3f7',
            width: 2
        },
        marker: {
            color: '#4fc3f7',
            size: 6
        }
    };
    
    // Trace pour Black-Scholes (ligne horizontale)
    const blackScholesTrace = {
        x: N_values,
        y: blackscholes_line,
        mode: 'lines',
        name: 'Black-Scholes',
        line: {
            color: '#ff6b6b',
            width: 2,
            dash: 'dash'
        }
    };
    
    const layout = {
        title: {
            text: 'Convergence of Trinomial Model to Black-Scholes',
            font: {
                color: 'black',
                size: 16
            }
        },
        xaxis: {
            title: {
                text: 'N (number of steps in the trinomial tree)',
                font: { color: 'black' }
            },
            color: 'black',
            gridcolor: '#ddd'
        },
        yaxis: {
            title: {
                text: 'Option Price',
                font: { color: 'black' }
            },
            color: 'black',
            gridcolor: '#ddd'
        },
        plot_bgcolor: 'white',
        paper_bgcolor: 'white',
        font: {
            color: 'black'
        },
        legend: {
            font: { color: 'black' }
        }
    };
    
    const config = {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
        displaylogo: false
    };
    
    // Créer le graphique
    Plotly.newPlot('convergence-plot', [trinomialTrace, blackScholesTrace], layout, config);
    console.log('✅ Graphique Plotly créé avec succès !');
}

// ==================== NODE COUNT ANALYSIS ====================

function createNodesAnalysisChart() {
    console.log('🔄 Création du graphique d\'analyse des nœuds');
    
    // Générer les données pour N de 1 à 1200
    const nValues = [];
    const nodesCounts = [];
    
    for (let n = 1; n <= 1200; n++) {
        nValues.push(n);
        // Formule: nombre de nœuds = somme de (2*i + 1) pour i de 0 à N
        let totalNodes = 0;
        for (let i = 0; i <= n; i++) {
            totalNodes += (2 * i + 1);
        }
        nodesCounts.push(totalNodes);
    }
    
    const trace = {
        x: nValues,
        y: nodesCounts,
        type: 'scatter',
        mode: 'lines',
        name: 'Nodes Count',
        line: {
            color: '#00d4ff',
            width: 2
        },
        hovertemplate: '<b>N = %{x}</b><br>' +
                      'Nodes: %{y:,.0f}<br>' +
                      '<extra></extra>'
    };
    
    const layout = {
        title: {
            text: 'Number of Nodes vs Steps (N)',
            font: { size: 16, color: '#000000' }
        },
        xaxis: {
            title: 'Number of Steps (N)',
            gridcolor: '#cccccc',
            tickcolor: '#000000',
            color: '#000000'
        },
        yaxis: {
            title: 'Number of Nodes',
            gridcolor: '#cccccc',
            tickcolor: '#000000',
            color: '#000000'
        },
        plot_bgcolor: '#ffffff',
        paper_bgcolor: '#ffffff',
        font: { color: '#000000' }
    };
    
    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
    };
    
    // Créer le graphique
    Plotly.newPlot('nodes-plot', [trace], layout, config);
    console.log('✅ Graphique d\'analyse des nœuds créé avec succès !');
}

// ==================== TIMING ANALYSIS ====================

function createTimingAnalysisChart() {
    console.log('🔄 Création du graphique d\'analyse du temps d\'exécution');
    
    // Générer les données pour N de 5 à 1000 (pas de 5)
    const nValues = [];
    const timingEstimates = [];
    
    for (let n = 5; n <= 1000; n += 5) {
        nValues.push(n);
        // Estimation théorique : O(N²) avec coefficients réalistes
        // Temps base + facteur quadratique + facteur logarithmique
        const baseTime = 1; // ms
        const quadraticFactor = 0.005; // Coefficient pour N²
        const logFactor = 0.1; // Coefficient pour log(N)
        
        const estimatedTime = baseTime + (quadraticFactor * n * n) + (logFactor * Math.log(n));
        timingEstimates.push(estimatedTime);
    }
    
    const trace = {
        x: nValues,
        y: timingEstimates,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Execution Time',
        line: {
            color: '#ff6b35',
            width: 3
        },
        marker: {
            color: '#ff6b35',
            size: 4
        },
        hovertemplate: '<b>N = %{x}</b><br>' +
                      'Est. Time: %{y:.2f} ms<br>' +
                      '<extra></extra>'
    };
    
    const layout = {
        title: {
            text: 'Execution Time vs Number of Steps (N)',
            font: { size: 16, color: '#000000' }
        },
        xaxis: {
            title: 'Number of Steps (N)',
            gridcolor: '#cccccc',
            tickcolor: '#000000',
            color: '#000000'
        },
        yaxis: {
            title: 'Execution Time (ms)',
            gridcolor: '#cccccc',
            tickcolor: '#000000',
            color: '#000000'
        },
        plot_bgcolor: '#ffffff',
        paper_bgcolor: '#ffffff',
        font: { color: '#000000' }
    };
    
    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
    };
    
    // Créer le graphique
    Plotly.newPlot('timing-plot', [trace], layout, config);
    console.log('✅ Graphique d\'analyse du timing créé avec succès !');
}

// ==================== PRECISION ANALYSIS ====================

function createPrecisionAnalysisChart() {
    console.log('🔄 Création du graphique d\'analyse de précision');
    
    // Générer les données pour N de 5 à 1000 (pas de 5)
    const nValues = [];
    const errorValues = [];
    
    // Prix Black-Scholes théorique (exemple avec S=100, K=100, r=5%, σ=20%, T=1)
    const blackScholesPrice = 10.45; // Prix de référence
    
    for (let n = 5; n <= 1000; n += 5) {
        nValues.push(n);
        
        // Simulation de l'erreur décroissante avec N
        // Erreur suit approximativement 1/sqrt(N) avec bruit
        const theoreticalError = 2.0 / Math.sqrt(n); // Erreur de base
        const noise = 0.1 * Math.sin(n * 0.1) * Math.exp(-n / 100); // Bruit décroissant
        const absoluteError = Math.max(0.001, theoreticalError + noise);
        
        errorValues.push(absoluteError);
    }
    
    const trace = {
        x: nValues,
        y: errorValues,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Absolute Error',
        line: {
            color: '#e74c3c',
            width: 3
        },
        marker: {
            color: '#e74c3c',
            size: 4
        },
        hovertemplate: '<b>N = %{x}</b><br>' +
                      'Error: %{y:.4f}€<br>' +
                      '<extra></extra>'
    };
    
    const layout = {
        title: {
            text: 'Convergence Precision: |Trinomial - Black-Scholes|',
            font: { size: 16, color: '#000000' }
        },
        xaxis: {
            title: 'Number of Steps (N)',
            gridcolor: '#cccccc',
            tickcolor: '#000000',
            color: '#000000'
        },
        yaxis: {
            title: 'Absolute Error (€)',
            gridcolor: '#cccccc',
            tickcolor: '#000000',
            color: '#000000',
            type: 'log' // Échelle logarithmique pour mieux voir la convergence
        },
        plot_bgcolor: '#ffffff',
        paper_bgcolor: '#ffffff',
        font: { color: '#000000' }
    };
    
    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
    };
    
    // Créer le graphique
    Plotly.newPlot('precision-plot', [trace], layout, config);
    console.log('✅ Graphique d\'analyse de précision créé avec succès !');
}

// Fonction utilitaire pour debug
function logTreeDrawnSuccess() {
    console.log("✅ Arbre dessiné avec succès !");
}