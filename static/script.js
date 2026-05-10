// ======================== EXISTING FUNCTIONS ========================
async function submitComplaint() {
    const text = document.getElementById("complaintText").value;
    if (!text.trim()) {
        document.getElementById("complaintResponse").innerText = "Please enter a complaint.";
        return;
    }
    try {
        const response = await fetch("/complaint", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({text: text})
        });
        const data = await response.json();
        document.getElementById("complaintResponse").innerText = 
            "Department: " + (data.department || 'N/A') +
            "\nPriority: " + (data.priority || 'N/A') +
            "\n" + (data.message || '');
    } catch (error) {
        document.getElementById("complaintResponse").innerText = "Error: " + error.message;
    }
}

async function submitQuery() {
    const question = document.getElementById("queryText").value;
    if (!question.trim()) {
        document.getElementById("queryResponse").innerText = "Please enter a question.";
        return;
    }
    try {
        const response = await fetch("/query", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({question: question})
        });
        const data = await response.json();
        document.getElementById("queryResponse").innerText = data.answer || "No answer received.";
    } catch (error) {
        document.getElementById("queryResponse").innerText = "Error: " + error.message;
    }
}

// ======================== NEW: TRACK COMPLAINT ========================
async function trackComplaint() {
    const complaintId = document.getElementById("trackId").value.trim();
    const trackDiv = document.getElementById("trackResponse");
    if (!complaintId) {
        trackDiv.innerHTML = '<span class="text-red-500">Please enter a Complaint ID.</span>';
        trackDiv.classList.remove('hidden');
        return;
    }
    try {
        const response = await fetch(`/track/${complaintId}`);
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.error || 'Not found');
        }
        const data = await response.json();
        // Build display
        let html = `<div class="space-y-1">
            <p><span class="font-semibold">ID:</span> ${data.complaint_id || ''}</p>
            <p><span class="font-semibold">Department:</span> ${data.department || ''}</p>
            <p><span class="font-semibold">Status:</span> 
                <span class="inline-block px-2 py-0.5 rounded-full text-xs font-medium 
                    ${data.status === 'Resolved' ? 'bg-green-100 text-green-800' : 
                      data.status === 'In Progress' ? 'bg-blue-100 text-blue-800' : 
                      'bg-yellow-100 text-yellow-800'}">
                    ${data.status || ''}
                </span>
            </p>
            <p><span class="font-semibold">Priority:</span> ${data.priority || ''}</p>
            <p><span class="font-semibold">Sentiment:</span> ${data.sentiment || ''}</p>
            <p><span class="font-semibold">Resolution note:</span> ${data.resolution || '—'}</p>`;
        if (data.resolved_at) {
            html += `<p><span class="font-semibold">Resolved on:</span> ${new Date(data.resolved_at).toLocaleString()}</p>`;
        }
        html += `</div>`;
        trackDiv.innerHTML = html;
        trackDiv.classList.remove('hidden');
    } catch (error) {
        trackDiv.innerHTML = `<span class="text-red-500">Error: ${error.message}</span>`;
        trackDiv.classList.remove('hidden');
    }
}

// ======================== NEW: FEEDBACK SUBMISSION ========================
async function submitFeedback() {
    const complaintId = document.getElementById("feedbackId").value.trim();
    // Get selected rating
    const ratingRadios = document.querySelectorAll('input[name="rating"]');
    let rating = null;
    for (let radio of ratingRadios) {
        if (radio.checked) {
            rating = radio.value;
            break;
        }
    }
    const comment = document.getElementById("feedbackComment").value.trim();
    const responseDiv = document.getElementById("feedbackResponse");

    if (!complaintId) {
        responseDiv.innerHTML = '<span class="text-red-500">Please enter a Complaint ID.</span>';
        return;
    }
    if (!rating) {
        responseDiv.innerHTML = '<span class="text-red-500">Please select a star rating.</span>';
        return;
    }

    try {
        const res = await fetch("/feedback", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                complaint_id: complaintId,
                rating: parseInt(rating),
                comment: comment
            })
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.error || 'Feedback submission failed');
        }
        const data = await res.json();
        responseDiv.innerHTML = '<span class="text-green-600 font-medium">✅ Thank you! Your feedback has been recorded.</span>';
        // Clear inputs
        document.getElementById("feedbackId").value = '';
        document.getElementById("feedbackComment").value = '';
        // Uncheck stars
        ratingRadios.forEach(r => r.checked = false);
    } catch (error) {
        responseDiv.innerHTML = `<span class="text-red-500">Error: ${error.message}</span>`;
    }
}