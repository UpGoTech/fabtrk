let currentEvent = null;
let participantModal = null;

// ============== GLOBAL FUNCTIONS ==============

// function openParticipantModal() {
//     console.log("openParticipantModal called");
//     console.log("currentEvent:", currentEvent);
    
//     if (!currentEvent) {
//         alert("Save event first!");
//         return;
//     }
    
//     document.getElementById("p-name").value = "";
//     document.getElementById("p-email").value = "";
//     document.getElementById("p-phone").value = "";
    
//     // Reset to contact search view
//     document.getElementById("select-contact-section").style.display = "block";
//     document.getElementById("manual-entry-section").style.display = "none";
//     document.getElementById("contact-search").value = "";
//     document.getElementById("contact-results").innerHTML = '<p class="text-muted text-center py-3">No Results</p>';
    
//     if (participantModal) {
//         participantModal.show();
//     } else {
//         alert("Modal not ready, please refresh and try again");
//     }
// }

function openParticipantModal() {
    console.log("openParticipantModal called");
    console.log("currentEvent:", currentEvent);

    // Clear participant fields
    document.getElementById("p-name").value = "";
    document.getElementById("p-email").value = "";
    document.getElementById("p-phone").value = "";

    // Reset to contact search view
    document.getElementById("select-contact-section").style.display = "block";
    document.getElementById("manual-entry-section").style.display = "none";
    document.getElementById("contact-search").value = "";
    document.getElementById("contact-results").innerHTML = '<p class="text-muted text-center py-3">No Results</p>';

    // Optional: add a paragraph for guidance
    const modalBody = document.querySelector("#participantModal .modal-body");
    const existingPara = modalBody.querySelector(".custom-info-paragraph");
    if (!existingPara) {
        const p = document.createElement("p");
        p.className = "custom-info-paragraph text-primary";
        p.innerText = "You can add participants even before saving the event. They will be linked once the event is saved.";
        modalBody.prepend(p);
    }

    // Show modal
    if (participantModal) {
        participantModal.show();
    } else {
        alert("Modal not ready, please refresh and try again");
    }
}


// ============== CONTACT SELECTION FUNCTIONS ==============

function createNewContact() {
    // Hide search section, show manual entry
    document.getElementById("select-contact-section").style.display = "none";
    document.getElementById("manual-entry-section").style.display = "block";
    document.getElementById("p-name").focus();
}

function backToContactSearch() {
    // Show search section, hide manual entry
    document.getElementById("select-contact-section").style.display = "block";
    document.getElementById("manual-entry-section").style.display = "none";
    
    // Clear manual entry fields
    document.getElementById("p-name").value = "";
    document.getElementById("p-email").value = "";
    document.getElementById("p-phone").value = "";
}

function searchContacts() {
    const searchTerm = document.getElementById("contact-search").value.toLowerCase();
    const resultsDiv = document.getElementById("contact-results");
    
    if (!searchTerm) {
        resultsDiv.innerHTML = '<p class="text-muted text-center py-3">No Results</p>';
        return;
    }
    
    // Sample contacts data
    const sampleContacts = [
        { name: "Rajesh Kumar", email: "rajesh@example.com", phone: "9876543210" },
        { name: "Priya Singh", email: "priya@example.com", phone: "9123456789" },
        { name: "Amit Patel", email: "amit@example.com", phone: "8765432109" },
        { name: "Neha Sharma", email: "neha@example.com", phone: "7654321098" },
    ];
    
    // Filter contacts
    const filtered = sampleContacts.filter(c => 
        c.name.toLowerCase().includes(searchTerm) || 
        c.email.toLowerCase().includes(searchTerm)
    );
    
    if (filtered.length === 0) {
        resultsDiv.innerHTML = '<p class="text-muted text-center py-3">No Results</p>';
        return;
    }
    
    // Display results
    let html = '<div class="list-group">';
    filtered.forEach(contact => {
        html += `
            <button type="button" class="list-group-item list-group-item-action text-start" 
                    onclick="selectContact('${contact.name}', '${contact.email}', '${contact.phone}')">
                <div class="fw-bold">${contact.name}</div>
                <small class="text-muted">${contact.email}</small>
            </button>
        `;
    });
    html += '</div>';
    
    resultsDiv.innerHTML = html;
}

function selectContact(name, email, phone) {
    // Fill manual entry fields
    document.getElementById("p-name").value = name;
    document.getElementById("p-email").value = email;
    document.getElementById("p-phone").value = phone;
    
    // Switch to manual entry section
    document.getElementById("select-contact-section").style.display = "none";
    document.getElementById("manual-entry-section").style.display = "block";
}

// Init modal AFTER page load
document.addEventListener("DOMContentLoaded", () => {
    // Wait for Bootstrap to be available
    setTimeout(() => {
        try {
            const modalElement = document.getElementById("participantModal");
            if (modalElement) {
                participantModal = new bootstrap.Modal(modalElement);
                console.log("Modal initialized successfully");
            } else {
                console.error("Modal element not found");
            }
        } catch (error) {
            console.error("Error initializing modal:", error);
        }
    }, 100);

    // Save Event
    const eventForm = document.getElementById("event-form");
    if (eventForm) {
        eventForm.addEventListener("submit", function (e) {
            e.preventDefault();

            const subject = document.getElementById("subject").value;
            const starts_on = document.getElementById("starts_on").value;
            
            console.log("Form submitted - Subject:", subject, "Starts On:", starts_on);
            
            if (!subject || !starts_on) {
                alert("Subject and Start date are required!");
                return;
            }

            // Create event object
            const eventObj = {
                id: "EVENT-" + Date.now(),
                subject: subject,
                starts_on: starts_on,
                ends_on: document.getElementById("ends_on").value,
                description: document.getElementById("description").value,
                category: document.getElementById("event_category").value,
                type: document.getElementById("event_type").value,
                status: document.getElementById("status").value,
                created_at: new Date().toLocaleString('en-IN')
            };

            // Save to localStorage
            let events = JSON.parse(localStorage.getItem("savedEvents") || "[]");
            events.push(eventObj);
            localStorage.setItem("savedEvents", JSON.stringify(events));
            
            // Save current event
            currentEvent = eventObj.id;
            localStorage.setItem("currentEvent", currentEvent);
            
            console.log("Event saved:", eventObj);
            console.log("Current Event ID:", currentEvent);
            
            document.getElementById("msg").innerHTML =
                "<span class='text-success'>✓ Event Saved Successfully (ID: " + currentEvent + ")</span>";
        });
    }

    // Save participant
    document.getElementById("save-participant").addEventListener("click", () => {
        const pName = document.getElementById("p-name").value;
        
        if (!pName) {
            alert("Participant name is required");
            return;
        }

        // Create participant object
        const participant = {
            id: "PART-" + Date.now(),
            event_id: currentEvent,
            name: pName,
            email: document.getElementById("p-email").value,
            phone: document.getElementById("p-phone").value,
            added_at: new Date().toLocaleString('en-IN')
        };

        // Save to localStorage
        let participants = JSON.parse(localStorage.getItem("eventParticipants") || "[]");
        participants.push(participant);
        localStorage.setItem("eventParticipants", JSON.stringify(participants));
        
        console.log("Participant added:", participant);
        
        // Clear inputs
        document.getElementById("p-name").value = "";
        document.getElementById("p-email").value = "";
        document.getElementById("p-phone").value = "";
        
        // Close modal
        if (participantModal) {
            participantModal.hide();
        }
        
        alert("✓ Participant Added Successfully!");
    });
});

// ============== CONTACT SELECTION FUNCTIONS ==============

function createNewContact() {
    // Hide search section, show manual entry
    document.getElementById("select-contact-section").style.display = "none";
    document.getElementById("manual-entry-section").style.display = "block";
    document.getElementById("p-name").focus();
}

function backToContactSearch() {
    // Show search section, hide manual entry
    document.getElementById("select-contact-section").style.display = "block";
    document.getElementById("manual-entry-section").style.display = "none";
    
    // Clear manual entry fields
    document.getElementById("p-name").value = "";
    document.getElementById("p-email").value = "";
    document.getElementById("p-phone").value = "";
}

function searchContacts() {
    const searchTerm = document.getElementById("contact-search").value.toLowerCase();
    const resultsDiv = document.getElementById("contact-results");
    
    if (!searchTerm) {
        resultsDiv.innerHTML = '<p class="text-muted text-center py-3">No Results</p>';
        return;
    }
    
    // Sample contacts data
    const sampleContacts = [
        { name: "Rajesh Kumar", email: "rajesh@example.com", phone: "9876543210" },
        { name: "Priya Singh", email: "priya@example.com", phone: "9123456789" },
        { name: "Amit Patel", email: "amit@example.com", phone: "8765432109" },
        { name: "Neha Sharma", email: "neha@example.com", phone: "7654321098" },
    ];
    
    // Filter contacts
    const filtered = sampleContacts.filter(c => 
        c.name.toLowerCase().includes(searchTerm) || 
        c.email.toLowerCase().includes(searchTerm)
    );
    
    if (filtered.length === 0) {
        resultsDiv.innerHTML = '<p class="text-muted text-center py-3">No Results</p>';
        return;
    }
    
    // Display results
    let html = '<div class="list-group">';
    filtered.forEach(contact => {
        html += `
            <button type="button" class="list-group-item list-group-item-action text-start" 
                    onclick="selectContact('${contact.name}', '${contact.email}', '${contact.phone}')">
                <div class="fw-bold">${contact.name}</div>
                <small class="text-muted">${contact.email}</small>
            </button>
        `;
    });
    html += '</div>';
    
    resultsDiv.innerHTML = html;
}

function selectContact(name, email, phone) {
    // Fill manual entry fields
    document.getElementById("p-name").value = name;
    document.getElementById("p-email").value = email;
    document.getElementById("p-phone").value = phone;
    
    // Switch to manual entry section
    document.getElementById("select-contact-section").style.display = "none";
    document.getElementById("manual-entry-section").style.display = "block";
}

function printEvent() {
    if (!currentEvent) {
        alert("Save event first");
        return;
    }
    alert("Print function: Event ID - " + currentEvent);
    // window.print();
}

function emailEvent() {
    if (!currentEvent) {
        alert("Save event first");
        return;
    }
    alert("Email function for Event: " + currentEvent);
}

function jumpToField() {
    alert("Jump to field - Select field name");
}

function showLinks() {
    if (!currentEvent) {
        alert("Save event first");
        return;
    }
    alert("Showing links for Event: " + currentEvent);
}

function duplicateEvent() {
    if (!currentEvent) {
        alert("Save event first");
        return;
    }
    alert("Duplicate Event: " + currentEvent);
}

function copyClipboard() {
    if (!currentEvent) {
        alert("Save event first");
        return;
    }
    navigator.clipboard.writeText(currentEvent);
    alert("Event ID copied to clipboard: " + currentEvent);
}

function reloadEvent() {
    location.reload();
}

function remindMe() {
    if (!currentEvent) {
        alert("Save event first");
        return;
    }
    alert("Reminder set for Event: " + currentEvent);
}

function undoEvent() {
    alert("Undo function");
}

function redoEvent() {
    alert("Redo function");
}

function customizeForm() {
    alert("Customize form - Opening customization panel");
}

function editDocType() {
    alert("Edit DocType - This opens the DocType editor");
}

function createNewEvent() {
    if (confirm("Create new event? Current data will be lost if not saved.")) {
        document.getElementById("event-form").reset();
        currentEvent = null;
        document.getElementById("msg").innerHTML = "";
        document.getElementById("add-participant-btn").disabled = true;
    }
}
