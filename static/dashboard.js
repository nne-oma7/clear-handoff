
const caseList = document.getElementById("case-list");
const searchInput = document.getElementById("search-input");
const statusFilter = document.getElementById("status-filter");
const refreshButton = document.getElementById("refresh-button");

const noSelection = document.getElementById("no-selection");
const complaintDetail = document.getElementById("complaint-detail");

const statusEditor = document.getElementById("status-editor-select");
const saveStatusButton = document.getElementById("save-status-button");
const copyReportButton = document.getElementById("copy-report-button");
const statusFeedback = document.getElementById("status-feedback");

let complaints = [];
let selectedComplaint = null;

const STATUS_LABELS = {
    received: "Received",
    awaiting_information: "Awaiting information",
    under_investigation: "Under investigation",
    ready_for_review: "Ready for review",
    escalated_to_engineering: "Escalated to engineering",
    resolved: "Resolved"
};

function formatStatus(status) {
    return STATUS_LABELS[status] || String(status || "Unknown").replaceAll("_", " ");
}

function formatReference(id) {
    return `CH-${String(id).padStart(6, "0")}`;
}

function formatDate(value) {
    if (!value) return "Not available";

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return String(value);
    }

    return date.toLocaleString();
}

function setText(id, value) {
    document.getElementById(id).textContent = value ?? "";
}

function showError(message) {
    caseList.replaceChildren();

    const error = document.createElement("p");
    error.className = "error-message";
    error.textContent = message;

    caseList.appendChild(error);
}

async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {})
        }
    });

    if (!response.ok) {
        const errorBody = await response.text();
        throw new Error(
            `Request failed (${response.status}). ${errorBody.slice(0, 250)}`
        );
    }

    return response.json();
}

function getOriginalMessage(complaint) {
    return complaint.original_complaint
        ?? complaint.original_message
        ?? complaint.message
        ?? "Original complaint not available.";
}

function getMissingInformation(complaint) {
    let missing = complaint.missing_information ?? [];

    // Some database implementations store JSON arrays as strings.
    if (typeof missing === "string") {
        try {
            missing = JSON.parse(missing);
        } catch {
            missing = [];
        }
    }

    return Array.isArray(missing) ? missing : [];
}

function getProvidedDetails(complaint) {
    let details = complaint.customer_provided_details
        ?? complaint.answers
        ?? {};

    if (typeof details === "string") {
        try {
            details = JSON.parse(details);
        } catch {
            return { "Details": details };
        }
    }

    return details && typeof details === "object" ? details : {};
}

function formatFieldName(name) {
    return String(name)
        .replaceAll("_", " ")
        .replace(/\b\w/g, character => character.toUpperCase());
}

function renderProvidedDetails(details) {
    const container = document.getElementById("provided-details");
    container.replaceChildren();

    const entries = Object.entries(details).filter(([, value]) => {
        return value !== null && value !== undefined && value !== "";
    });

    if (entries.length === 0) {
        container.textContent = "No additional answers were provided.";
        return;
    }

    const list = document.createElement("ul");
    list.className = "detail-list";

    for (const [key, value] of entries) {
        const item = document.createElement("li");
        const label = document.createElement("strong");

        label.textContent = `${formatFieldName(key)}: `;
        item.appendChild(label);

        const valueText = Array.isArray(value)
            ? value.join(", ")
            : typeof value === "object"
                ? JSON.stringify(value)
                : String(value);

        item.appendChild(document.createTextNode(valueText));
        list.appendChild(item);
    }

    container.appendChild(list);
}


function renderContactDetails(contact) {
    const container = document.getElementById("contact-details");
    container.replaceChildren();

    const rows = [
        ["Name", contact?.name],
        ["Email", contact?.email],
        ["Phone", contact?.phone]
    ].filter(([, value]) => value);

    if (rows.length === 0) {
        container.textContent = "No contact details were provided.";
        return;
    }

    const list = document.createElement("ul");
    list.className = "detail-list";

    for (const [label, value] of rows) {
        const item = document.createElement("li");
        const strong = document.createElement("strong");

        strong.textContent = `${label}: `;
        item.append(strong, document.createTextNode(value));
        list.appendChild(item);
    }

    container.appendChild(list);
}   


function renderMissingInformation(missing) {
    const container = document.getElementById("missing-details");
    container.replaceChildren();

    setText("detail-missing-count", String(missing.length));
    setText("missing-badge", String(missing.length));

    if (missing.length === 0) {
        container.textContent = "No missing information has been flagged.";
        return;
    }

    const list = document.createElement("div");
    list.className = "missing-list";

    for (const item of missing) {
        const card = document.createElement("div");
        card.className = "missing-item";

        const question = document.createElement("strong");
        const reason = document.createElement("span");

        if (typeof item === "string") {
            question.textContent = item;
            reason.textContent = "Not provided";
        } else {
            question.textContent =
                item.question ?? item.label ?? item.key ?? "Additional information needed";

            reason.textContent =
                item.reason ?? "This information was not provided.";
        }

        card.append(question, reason);
        list.appendChild(card);
    }

    container.appendChild(list);
}

function createStatusPill(status) {
    const pill = document.createElement("span");
    pill.className = `status-pill status-${status || "unknown"}`;
    pill.textContent = formatStatus(status);
    return pill;
}

function renderComplaintList() {
    const searchTerm = searchInput.value.trim().toLowerCase();
    const selectedStatus = statusFilter.value;

    const filtered = complaints.filter(complaint => {
        const id = String(complaint.id ?? "");
        const reference = formatReference(id);
        const category = String(complaint.category ?? "");
        const message = getOriginalMessage(complaint);
        const status = String(complaint.status ?? "");

        const contact = complaint.customer_contact ?? {};

        const matchesSearch = [
            id,
            reference,
            category,
            message,
            contact.name ?? "",
            contact.email ?? "",
            contact.phone ?? ""
        ].some(value => value.toLowerCase().includes(searchTerm));

        const matchesStatus =
            selectedStatus === "all" || status === selectedStatus;

        return matchesSearch && matchesStatus;
    });

    caseList.replaceChildren();
    setText("visible-count", String(filtered.length));

    if (filtered.length === 0) {
        const empty = document.createElement("p");
        empty.className = "sidebar-empty";
        empty.textContent = complaints.length
            ? "No tickets match your search or filter."
            : "No complaints have been submitted yet.";

        caseList.appendChild(empty);
        return;
    }

    for (const complaint of filtered) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "case-card";

        if (selectedComplaint && complaint.id === selectedComplaint.id) {
            button.classList.add("selected");
        }

        const top = document.createElement("div");
        top.className = "case-card-top";

        const reference = document.createElement("span");
        reference.className = "case-reference";
        reference.textContent = formatReference(complaint.id);

        top.append(reference, createStatusPill(complaint.status));

        const category = document.createElement("p");
        category.className = "case-category";
        category.textContent = formatFieldName(
            complaint.category || "General complaint"
        );

        const preview = document.createElement("p");
        preview.className = "case-preview";
        preview.textContent = getOriginalMessage(complaint);

        const bottom = document.createElement("div");
        bottom.className = "case-card-bottom";

        const date = document.createElement("span");
        date.className = "case-date";
        date.textContent = formatDate(complaint.created_at);

        bottom.appendChild(date);
        button.append(top, category, preview, bottom);

        button.addEventListener("click", () => {
            openComplaint(complaint.id);
        });

        caseList.appendChild(button);
    }
}

function updateStatistics() {
    setText("total-count", String(complaints.length));

    setText(
        "awaiting-count",
        String(complaints.filter(c => c.status === "awaiting_information").length)
    );

    setText(
        "investigation-count",
        String(complaints.filter(c => c.status === "under_investigation").length)
    );

    setText(
        "resolved-count",
        String(complaints.filter(c => c.status === "resolved").length)
    );
}

async function loadComplaints() {
    try {
        refreshButton.disabled = true;
        const data = await apiRequest("/complaints");

        complaints = Array.isArray(data)
            ? data
            : data.complaints ?? data.items ?? [];

        updateStatistics();
        renderComplaintList();

        if (selectedComplaint) {
            const stillExists = complaints.some(
                complaint => complaint.id === selectedComplaint.id
            );

            if (stillExists) {
                await openComplaint(selectedComplaint.id, false);
            } else {
                selectedComplaint = null;
                complaintDetail.hidden = true;
                noSelection.hidden = false;
            }
        }
    } catch (error) {
        showError(`Could not load tickets. ${error.message}`);
    } finally {
        refreshButton.disabled = false;
    }
}

async function openComplaint(id, updateList = true) {
    try {
        statusFeedback.textContent = "";

        const complaint = await apiRequest(`/complaints/${id}`);
        selectedComplaint = complaint;

        noSelection.hidden = true;
        complaintDetail.hidden = false;

        setText("detail-title", `Complaint ${formatReference(complaint.id)}`);
        setText("detail-reference", formatReference(complaint.id));
        setText(
            "detail-category",
            formatFieldName(complaint.category || "General complaint")
        );
        setText("detail-date", formatDate(complaint.created_at));
        setText("original-message", getOriginalMessage(complaint));

        renderContactDetails(complaint.customer_contact);
        renderProvidedDetails(getProvidedDetails(complaint));
        renderMissingInformation(getMissingInformation(complaint));

        setText(
            "investigation-note",
            complaint.investigation_note
                ?? "No investigation note has been added."
        );

        statusEditor.value = complaint.status || "received";

        saveStatusButton.disabled = false;
        copyReportButton.disabled = false;

        if (updateList) {
            renderComplaintList();
        }
    } catch (error) {
        statusFeedback.textContent = `Could not open this ticket: ${error.message}`;
    }
}

async function saveComplaintStatus() {
    if (!selectedComplaint) return;

    try {
        saveStatusButton.disabled = true;
        statusFeedback.textContent = "Saving status...";

        const newStatus = statusEditor.value;

        await apiRequest(
            `/complaints/${selectedComplaint.id}/status`,
            {
                method: "PATCH",
                body: JSON.stringify({ status: newStatus })
            }
        );

        await loadComplaints();
        statusFeedback.textContent = "Status updated successfully.";
    } catch (error) {
        statusFeedback.textContent = `Could not update status: ${error.message}`;
    } finally {
        saveStatusButton.disabled = false;
    }
}

async function copyHandoffReport() {
    if (!selectedComplaint) return;

    const complaint = selectedComplaint;
    const missing = getMissingInformation(complaint);
    const details = getProvidedDetails(complaint);

    const detailsText = Object.entries(details)
        .map(([key, value]) => {
            const readableValue = typeof value === "object"
                ? JSON.stringify(value)
                : String(value);

            return `${formatFieldName(key)}: ${readableValue}`;
        })
        .join("\n");

    const missingText = missing.length
        ? missing.map(item => {
            if (typeof item === "string") return `- ${item}`;
            return `- ${item.question ?? item.label ?? item.key ?? "Additional information"}${item.reason ? ` (${item.reason})` : ""}`;
        }).join("\n")
        : "No missing information flagged.";

    const report = [
        "CLEARHANDOFF — ENGINEERING HANDOFF",
        `Ticket: ${formatReference(complaint.id)}`,
        `Category: ${formatFieldName(complaint.category || "General complaint")}`,
        `Status: ${formatStatus(complaint.status)}`,
        `Submitted: ${formatDate(complaint.created_at)}`,
        "",
        "ORIGINAL CUSTOMER COMPLAINT",
        getOriginalMessage(complaint),
        "",
        "CUSTOMER-PROVIDED DETAILS",
        detailsText || "No additional answers provided.",
        "",
        "MISSING INFORMATION",
        missingText,
        "",
        "INVESTIGATION NOTE",
        complaint.investigation_note || "No investigation note has been added.",
        "",
        "Note: Customer-provided information has not necessarily been independently verified."
    ].join("\n");

    try {
        await navigator.clipboard.writeText(report);
        statusFeedback.textContent = "Handoff report copied to clipboard.";
    } catch {
        statusFeedback.textContent =
            "Clipboard access failed. Try opening the site in a secure browser context.";
    }
}

refreshButton.addEventListener("click", loadComplaints);
searchInput.addEventListener("input", renderComplaintList);
statusFilter.addEventListener("change", renderComplaintList);
saveStatusButton.addEventListener("click", saveComplaintStatus);
copyReportButton.addEventListener("click", copyHandoffReport);

loadComplaints();