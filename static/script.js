
const API = "";

const connectionStatus = document.getElementById("connectionStatus");
const systemStatus = document.getElementById("systemStatus");

// API request helper
async function request(url, options = {}) {
    const response = await fetch(API + url, options);

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "Request failed.");
    }

    return data;
}

// Display messages
function showMessage(element, message, isError = false) {
    element.innerHTML = "";

    const div = document.createElement("div");
    div.className = isError ? "message error" : "message";
    div.textContent = message;

    element.appendChild(div);
}

// Display JSON objects
function showObject(element, data) {
    element.innerHTML = "";

    const pre = document.createElement("pre");
    pre.style.whiteSpace = "pre-wrap";
    pre.style.overflowWrap = "anywhere";
    pre.textContent = JSON.stringify(data, null, 2);

    element.appendChild(pre);
}

// Connection status
async function checkConnection() {
    try {
        await request("/health");

        connectionStatus.textContent = "Connected";
        systemStatus.textContent = "Online";

        document.querySelector(".status-dot").style.background = "#35c98b";

    } catch (error) {
        connectionStatus.textContent = "Disconnected";
        systemStatus.textContent = "Offline";

        document.querySelector(".status-dot").style.background = "#e34f5a";
    }
}

// File selection
document.getElementById("documentFile").addEventListener("change", event => {
    const file = event.target.files[0];

    document.getElementById("fileName").textContent =
        file ? file.name : "No file selected";
});

// Upload and analyze document
document.getElementById("uploadForm").addEventListener("submit", async event => {
    event.preventDefault();

    const file = document.getElementById("documentFile").files[0];
    const output = document.getElementById("uploadResult");

    if (!file) {
        showMessage(output, "Please select a document.", true);
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    showMessage(output, "Uploading and analyzing document...");

    try {
        const data = await request("/documents/upload", {
            method: "POST",
            body: formData
        });

        renderUploadResult(data, output);

        // Refresh dashboard after successful upload
        await loadDashboard();

        document.getElementById("uploadForm").reset();
        document.getElementById("fileName").textContent = "No file selected";

    } catch (error) {
        showMessage(output, error.message, true);
    }
});

// Semantic search
document.getElementById("searchForm").addEventListener("submit", async event => {
    event.preventDefault();

    const output = document.getElementById("searchResults");
    const query = document.getElementById("searchQuery").value.trim();

    if (!query) {
        showMessage(output, "Please enter a search query.", true);
        return;
    }

    showMessage(output, "Searching invoices...");

    try {
        const data = await request("/search", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                query,
                top_k: 5
            })
        });

        output.innerHTML = "";

        if (!data.results || data.results.length === 0) {
            showMessage(output, "No matching invoices found.");
            return;
        }

        data.results.forEach(item => {
            const card = document.createElement("div");
            card.className = "result-card";

            const title = document.createElement("strong");
            title.textContent = item.invoice_id;

            const description = document.createElement("p");
            description.textContent = item.description;

            const score = document.createElement("p");
            score.textContent = "Similarity: " + item.similarity_score;

            card.append(title, description, score);
            output.appendChild(card);
        });

    } catch (error) {
        showMessage(output, error.message, true);
    }
});

// AI question answering
document.getElementById("askForm").addEventListener("submit", async event => {
    event.preventDefault();

    const output = document.getElementById("aiResult");
    const question = document.getElementById("question").value.trim();

    if (!question) {
        showMessage(output, "Please enter a question.", true);
        return;
    }

    showMessage(output, "DocuMind AI is analyzing your question...");

    try {
        const data = await request("/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ question })
        });

        output.innerHTML = "";

        const answer = document.createElement("div");
        answer.className = "result-card";

        const heading = document.createElement("strong");
        heading.textContent = "AI Answer";

        const paragraph = document.createElement("p");
        paragraph.textContent = data.answer;

        answer.append(heading, paragraph);
        output.appendChild(answer);

        if (data.evidence && data.evidence.length) {
            const evidenceHeading = document.createElement("h3");
            evidenceHeading.textContent = "Supporting Evidence";
            evidenceHeading.style.marginTop = "18px";

            output.appendChild(evidenceHeading);

            data.evidence.forEach(item => {
                const card = document.createElement("div");
                card.className = "result-card";

                const title = document.createElement("strong");
                title.textContent = item.invoice_id;

                const description = document.createElement("p");
                description.textContent = item.description;

                const score = document.createElement("p");
                score.textContent = "Similarity: " + item.similarity_score;

                card.append(title, description, score);
                output.appendChild(card);
            });
        }

    } catch (error) {
        showMessage(output, error.message, true);
    }
});

// Load invoices

async function loadInvoices() {
    const countElement = document.getElementById("invoiceCount");
    const output = document.getElementById("invoiceList");

    try {
        const data = await request("/invoices");

        countElement.textContent = data.total_invoices;
        output.innerHTML = "";

        if (!data.invoices || data.invoices.length === 0) {
            showMessage(output, "No invoices stored yet.");
            return;
        }

        data.invoices.forEach(invoice => {
            const card = document.createElement("div");
            card.className = "invoice-item";

            const header = document.createElement("div");
            header.className = "invoice-card-header";

            const title = document.createElement("h3");
            title.textContent = invoice.invoice_number;

            const risk = (invoice.risk_level || "UNKNOWN").toLowerCase();

            const badge = document.createElement("span");
            badge.className = `risk-badge ${risk}`;
            badge.textContent = `${risk.toUpperCase()} RISK`;

            header.append(title, badge);

            const details = document.createElement("p");
            details.textContent =
                `Vendor: ${invoice.vendor}`;

            const amount = document.createElement("p");
            amount.textContent =
                `Invoice Amount: ${invoice.currency} ${invoice.total_amount}`;

            const date = document.createElement("p");
            date.textContent =
                `Invoice Date: ${invoice.invoice_date || "Not available"}`;

            const po = document.createElement("p");
            po.textContent =
                `Purchase Order: ${invoice.purchase_order || "Not available"}`;

            const reasonHeading = document.createElement("h4");
            reasonHeading.textContent = "Risk Details";

            const reasonList = document.createElement("ul");
            reasonList.className = "issue-list";

            (invoice.risk_details || []).forEach(reason => {
                const li = document.createElement("li");
                li.textContent = reason;
                reasonList.appendChild(li);
            });

            if (invoice.po_amount !== null &&
                invoice.po_amount !== undefined) {
                const poAmount = document.createElement("p");
                poAmount.textContent =
                    `Purchase Order Amount: ${invoice.currency} ${invoice.po_amount}`;
                card.appendChild(poAmount);
            }

            card.append(
                header,
                details,
                amount,
                date,
                po,
                reasonHeading,
                reasonList
            );

            output.appendChild(card);
        });

    } catch (error) {
        countElement.textContent = "Error";
        showMessage(output, error.message, true);
    }
}

// Load invoice risk summary
async function loadRiskSummary() {
    try {
        const data = await request("/risk-summary");
        const risks = data.risk_counts || {};

        document.getElementById("highRiskCount").textContent =
            risks.HIGH ?? 0;

        document.getElementById("mediumRiskCount").textContent =
            risks.MEDIUM ?? 0;

        document.getElementById("lowRiskCount").textContent =
            risks.LOW ?? 0;

    } catch (error) {
        console.error("Risk summary error:", error);
    }
}

// Load complete dashboard
async function loadDashboard() {
    await Promise.all([
        loadInvoices(),
        loadRiskSummary()
    ]);
}


// ML anomaly detection
document.getElementById("anomalyButton").addEventListener("click", async () => {
    const output = document.getElementById("anomalyResults");

    showMessage(output, "Analyzing invoice records using machine learning...");

    try {
        const data = await request("/anomalies");
        renderAnomalyReport(data, output);

    } catch (error) {
        showMessage(output, error.message, true);
    }
});


function renderAnomalyReport(data, output) {
    function escapeHTML(value) {
        return String(value ?? "").replace(/[&<>"']/g, char => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        })[char]);
    }

    const results = data.results || [];

    const normalCount = results.filter(
        invoice => invoice.status_label === "NORMAL"
    ).length;

    const anomalyCount = results.filter(
        invoice => invoice.status_label === "ANOMALY"
    ).length;

    const notEvaluatedCount = results.filter(
        invoice => invoice.status_label === "NOT_EVALUATED"
    ).length;

    const statusColors = {
        NORMAL: "#15803d",
        ANOMALY: "#dc2626",
        NOT_EVALUATED: "#d97706"
    };

    const statusLabels = {
        NORMAL: "NORMAL",
        ANOMALY: "ANOMALY",
        NOT_EVALUATED: "NOT EVALUATED"
    };

    const summary = `
        <div style="
            display:grid;
            grid-template-columns:repeat(auto-fit,minmax(130px,1fr));
            gap:12px;
            margin-bottom:20px;
        ">
            <div class="stat-card">
                <h3>${data.records_analyzed}</h3>
                <p>Invoices Analyzed</p>
            </div>

            <div class="stat-card">
                <h3>${anomalyCount}</h3>
                <p>Anomalies Found</p>
            </div>

            <div class="stat-card">
                <h3>${normalCount}</h3>
                <p>Normal Invoices</p>
            </div>

            <div class="stat-card">
                <h3>${notEvaluatedCount}</h3>
                <p>Not Evaluated</p>
            </div>
        </div>
    `;

    const message = `
        <div style="
            padding:12px;
            margin-bottom:16px;
            border-radius:8px;
            background:#f3f4f6;
            color:#374151;
        ">
            <strong>Status:</strong> ${escapeHTML(data.status || "unknown")}
            <p>${escapeHTML(data.message || "")}</p>
            <small>Algorithm: ${escapeHTML(data.algorithm)}</small>
        </div>
    `;

    if (results.length === 0) {
        output.innerHTML = message +
            "<p>No invoices available for anomaly detection.</p>";
        return;
    }

    const rows = results.map(invoice => {
        const status = invoice.status_label || "NOT_EVALUATED";
        const color = statusColors[status] || "#6b7280";
        const label = statusLabels[status] || status;

        const amount = Number(invoice.total_amount).toLocaleString(
            "en-IN",
            { maximumFractionDigits: 2 }
        );

        const score = invoice.anomaly_score == null
            ? "—"
            : Number(invoice.anomaly_score).toFixed(4);

        return `
            <tr>
                <td>${escapeHTML(invoice.invoice_number)}</td>
                <td>${escapeHTML(invoice.vendor)}</td>
                <td>
                    ${escapeHTML(invoice.currency)}
                    ${amount}
                </td>
                <td>
                    <span style="
                        color:white;
                        background:${color};
                        padding:5px 9px;
                        border-radius:5px;
                        font-size:12px;
                        font-weight:bold;
                    ">
                        ${label}
                    </span>
                </td>
                <td>${score}</td>
            </tr>
        `;
    }).join("");

    output.innerHTML = `
        ${summary}
        ${message}

        <div style="overflow-x:auto;">
            <table style="
                width:100%;
                border-collapse:collapse;
                min-width:650px;
            ">
                <thead>
                    <tr>
                        <th>Invoice Number</th>
                        <th>Vendor</th>
                        <th>Amount</th>
                        <th>Status</th>
                        <th>Anomaly Score</th>
                    </tr>
                </thead>

                <tbody>
                    ${rows}
                </tbody>
            </table>
        </div>
    `;
}


// Render uploaded document analysis
function renderUploadResult(data, output) {
    output.innerHTML = "";

    const doc = data.document;
    const fields = doc.invoice_fields;
    const risk = (doc.overall_risk || "UNKNOWN").toLowerCase();

    const summary = document.createElement("div");
    summary.className = `risk-summary ${risk}`;

    const heading = document.createElement("h3");
    heading.textContent = "Invoice Analysis Complete";

    const badge = document.createElement("span");
    badge.className = `risk-badge ${risk}`;
    badge.textContent = `${doc.overall_risk} RISK`;

    summary.append(heading, badge);

    const grid = document.createElement("div");
    grid.className = "analysis-grid";

    const items = [
        ["Invoice Number", fields.invoice_number],
        ["Vendor", fields.vendor],
        ["Invoice Amount", `${fields.currency || ""} ${fields.total_amount ?? "N/A"}`],
        ["Invoice Date", fields.invoice_date],
        ["Purchase Order", fields.purchase_order],
        ["File Name", doc.original_filename]
    ];

    items.forEach(([label, value]) => {
        const item = document.createElement("div");
        item.className = "analysis-item";

        const small = document.createElement("small");
        small.textContent = label;

        const strong = document.createElement("strong");
        strong.textContent = value ?? "Not available";

        item.append(small, strong);
        grid.appendChild(item);
    });

    const checks = document.createElement("div");
    checks.className = "result-card";

    const validation = doc.validation;
    const duplicate = doc.duplicate_check;
    const po = doc.purchase_order_check;

    const checkHeading = document.createElement("h3");
    checkHeading.textContent = "Risk Checks";

    const checkList = document.createElement("ul");
    checkList.className = "issue-list";

    const checkItems = [
        `Validation: ${validation.risk_level} — ${
            validation.is_valid
                ? "All required fields are valid"
                : validation.issue_count + " issue(s) found"
        }`,
        `Duplicate check: ${
            duplicate.is_duplicate
                ? "Duplicate detected"
                : "No duplicate found"
        }`,
        `Purchase order: ${po.message}`
    ];

    checkItems.forEach(message => {
        const li = document.createElement("li");
        li.textContent = message;
        checkList.appendChild(li);
    });

    checks.append(checkHeading, checkList);

    if (po.difference !== undefined) {
        const difference = document.createElement("p");

        difference.textContent =
            `Amount difference: ${fields.currency || ""} ${po.difference}`;

        checks.appendChild(difference);
    }

    if (validation.issues?.length) {
        const issueHeading = document.createElement("h4");
        issueHeading.textContent = "Validation Issues";

        checks.appendChild(issueHeading);

        validation.issues.forEach(issue => {
            const p = document.createElement("p");
            p.textContent = issue.message;
            checks.appendChild(p);
        });
    }

    summary.appendChild(grid);
    summary.appendChild(checks);

    output.appendChild(summary);
}

// Refresh dashboard button
document.getElementById("refreshDashboard").addEventListener("click", async () => {
    await checkConnection();
    await loadDashboard();
});

// Initialize dashboard
checkConnection();
loadDashboard();