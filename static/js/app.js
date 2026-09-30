/**
 * MEDI-Q Frontend Application Logic
 * Smart Doctor Recommendation, Digital Token Booking & Queue Management
 */

// Application State
const state = {
    activePage: 'home',
    symptoms: {},
    selectedSymptoms: new Set(),
    emergencySymptomsSelected: [],
    doctors: [],
    recommendedSpec: null,
    activeUserBookings: [],
    currentQueueDoctorId: 1,
    adminDoctorId: 1,
    queuePollInterval: null,
    currentUserId: 1,
    currentUserName: "Rahul Sharma"
};

// Emergency symptoms mapping
const EMERGENCY_MAP = {
    "Chest Pain": "Potential acute cardiac event or heart disorder.",
    "Breathing Difficulty": "Potential severe respiratory distress or airway blockage.",
    "Fast / Irregular Heartbeat": "Potential cardiac arrhythmia or circulatory risk.",
    "Numbness": "Potential acute neurological condition or stroke symptom.",
    "Blood in Urine": "Potential acute renal or urinary emergency."
};

// DOM Initialization
document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

function initApp() {
    loadSymptoms();
    loadDoctors();
    loadMyTokens();
    setupEventListeners();
    
    // Set default date for booking form to today
    const today = new Date().toISOString().split('T')[0];
    const dateInput = document.getElementById('book-date');
    if (dateInput) dateInput.value = today;
}

// Navigation Handler
function navigateTo(pageId) {
    state.activePage = pageId;

    // Update Nav Button Active States
    document.querySelectorAll('.nav-btn').forEach(btn => {
        if (btn.dataset.target === pageId) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    // Toggle Page Views
    document.querySelectorAll('.page-view').forEach(page => {
        page.classList.remove('active');
    });

    const targetPage = document.getElementById(`page-${pageId}`);
    if (targetPage) {
        targetPage.classList.add('active');
    }

    // Handle Page Specific Initializations
    if (pageId === 'doctors') {
        if (!state.doctors.length) loadDoctors();
    } else if (pageId === 'my-token') {
        loadMyTokens();
    } else if (pageId === 'queue-status') {
        populateDoctorDropdowns();
        loadQueueData();
        startQueuePolling();
    } else if (pageId === 'admin') {
        populateDoctorDropdowns();
        loadAdminQueueData();
        stopQueuePolling();
    } else {
        stopQueuePolling();
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ==================== SYMPTOMS SELECTION ====================

async function loadSymptoms() {
    try {
        const response = await fetch('/api/symptoms');
        const data = await response.json();
        if (data.success) {
            state.symptoms = data.categories;
            renderSymptoms();
        }
    } catch (err) {
        console.error("Failed to load symptoms:", err);
    }
}

function renderSymptoms() {
    const container = document.getElementById('symptoms-categories-container');
    if (!container) return;

    container.innerHTML = '';

    for (const [category, symptomList] of Object.entries(state.symptoms)) {
        const catCard = document.createElement('div');
        catCard.className = 'symptom-category-card';

        // Choose Category Icon
        let iconClass = "fa-notes-medical";
        if (category === "General") iconClass = "fa-hospital-user";
        else if (category === "Respiratory") iconClass = "fa-lungs";
        else if (category === "Stomach & Digestive") iconClass = "fa-virus";
        else if (category === "Skin") iconClass = "fa-hand-dots";
        else if (category === "Heart & Circulation") iconClass = "fa-heart-pulse";
        else if (category === "Bone & Muscle") iconClass = "fa-bone";
        else if (category === "Eye") iconClass = "fa-eye";
        else if (category === "ENT") iconClass = "fa-ear-listen";
        else if (category === "Neurological") iconClass = "fa-brain";
        else if (category === "Dental") iconClass = "fa-tooth";
        else if (category === "Urinary") iconClass = "fa-droplet";

        const pillsHTML = symptomList.map(s => {
            const isSelected = state.selectedSymptoms.has(s.name);
            const isEmerg = s.is_emergency;
            return `
                <div class="symptom-pill ${isSelected ? 'selected' : ''} ${isEmerg ? 'emergency' : ''}" 
                     data-name="${s.name}" 
                     data-emerg="${isEmerg}"
                     onclick="toggleSymptomSelect('${s.name}', ${isEmerg})">
                    <span>${s.name} ${isEmerg ? '⚠️' : ''}</span>
                    <div class="check-icon"><i class="fa-solid fa-check"></i></div>
                </div>
            `;
        }).join('');

        catCard.innerHTML = `
            <div class="category-header">
                <i class="fa-solid ${iconClass}"></i> ${category} Symptoms
            </div>
            <div class="symptoms-pill-grid">
                ${pillsHTML}
            </div>
        `;

        container.appendChild(catCard);
    }
}

function toggleSymptomSelect(symptomName, isEmergency) {
    if (state.selectedSymptoms.has(symptomName)) {
        state.selectedSymptoms.delete(symptomName);
    } else {
        state.selectedSymptoms.add(symptomName);
    }

    updateSymptomSelectionUI();
    renderSymptoms();
}

function updateSymptomSelectionUI() {
    const countBadge = document.getElementById('selected-symptoms-count');
    const clearBtn = document.getElementById('btn-clear-symptoms');
    const findBtn = document.getElementById('btn-find-doctor');
    const tagsContainer = document.getElementById('selected-tags-container');

    const count = state.selectedSymptoms.size;
    if (countBadge) countBadge.textContent = count;
    
    if (clearBtn) clearBtn.style.display = count > 0 ? 'inline-block' : 'none';
    if (findBtn) findBtn.disabled = count === 0;

    if (tagsContainer) {
        if (count === 0) {
            tagsContainer.innerHTML = `<span class="placeholder-text">No symptoms selected yet. Click options above.</span>`;
        } else {
            tagsContainer.innerHTML = Array.from(state.selectedSymptoms).map(s => {
                const isEmerg = EMERGENCY_MAP[s] !== undefined;
                return `
                    <div class="tag-item ${isEmerg ? 'emergency' : ''}">
                        ${s}
                        <span class="remove-tag" onclick="toggleSymptomSelect('${s}', ${isEmerg})">&times;</span>
                    </div>
                `;
            }).join('');
        }
    }
}

function clearSelectedSymptoms() {
    state.selectedSymptoms.clear();
    updateSymptomSelectionUI();
    renderSymptoms();
}

function filterSymptoms() {
    const query = document.getElementById('symptom-search').value.toLowerCase().trim();
    document.querySelectorAll('.symptom-pill').forEach(pill => {
        const text = pill.dataset.name.toLowerCase();
        if (text.includes(query)) {
            pill.style.display = 'flex';
        } else {
            pill.style.display = 'none';
        }
    });
}

// Check Emergency symptoms and trigger AI Recommendation
function processSymptomsAndFindDoctor() {
    if (state.selectedSymptoms.size === 0) return;

    // Check emergency items
    state.emergencySymptomsSelected = [];
    state.selectedSymptoms.forEach(s => {
        if (EMERGENCY_MAP[s]) {
            state.emergencySymptomsSelected.push({
                symptom: s,
                reason: EMERGENCY_MAP[s]
            });
        }
    });

    if (state.emergencySymptomsSelected.length > 0) {
        // Show Emergency Modal Warning
        const emergencyList = document.getElementById('emergency-symptom-list');
        if (emergencyList) {
            emergencyList.innerHTML = state.emergencySymptomsSelected.map(item => `
                <div class="emergency-item">
                    <strong>• ${item.symptom}:</strong> ${item.reason}
                </div>
            `).join('');
        }
        document.getElementById('emergency-modal').style.display = 'flex';
    } else {
        proceedToDoctorRecommendation(false);
    }
}

function closeEmergencyModal() {
    document.getElementById('emergency-modal').style.display = 'none';
}

async function proceedToDoctorRecommendation(bypassedEmergency) {
    closeEmergencyModal();
    const selectedList = Array.from(state.selectedSymptoms);

    try {
        const response = await fetch('/api/recommend', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symptoms: selectedList })
        });
        const data = await response.json();

        if (data.success) {
            state.recommendedSpec = data.recommendation;
            state.doctors = data.doctors;

            // Render AI box
            const aiBox = document.getElementById('ai-recommendation-box');
            const aiTitle = document.getElementById('ai-recommended-spec');
            const aiConf = document.getElementById('ai-confidence-badge');
            const aiReason = document.getElementById('ai-reasoning-summary');

            if (aiBox && aiTitle) {
                aiTitle.textContent = data.recommendation.recommended_specialization;
                aiConf.textContent = `${data.recommendation.confidence}% AI Match`;
                aiReason.textContent = data.recommendation.reasoning;
                aiBox.style.display = 'block';
            }

            // Sync department filter dropdown
            const deptFilter = document.getElementById('department-filter');
            if (deptFilter) deptFilter.value = data.recommendation.recommended_specialization;

            renderDoctorsList(data.doctors);
            navigateTo('doctors');
        }
    } catch (err) {
        console.error("Failed to run AI recommendation:", err);
    }
}

// ==================== DOCTORS & SORTING ====================

async function loadDoctors() {
    try {
        const response = await fetch('/api/doctors');
        const data = await response.json();
        if (data.success) {
            state.doctors = data.doctors;
            renderDoctorsList(data.doctors);
            populateDoctorDropdowns();
        }
    } catch (err) {
        console.error("Error fetching doctors:", err);
    }
}

function filterDoctors() {
    const spec = document.getElementById('department-filter').value;
    const sort = document.getElementById('sort-filter').value;
    const search = document.getElementById('doctor-search-input').value;

    fetch(`/api/doctors?specialization=${encodeURIComponent(spec)}&sort_by=${sort}&search=${encodeURIComponent(search)}`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                state.doctors = data.doctors;
                renderDoctorsList(data.doctors);
            }
        });
}

function renderDoctorsList(doctorList) {
    const grid = document.getElementById('doctors-grid');
    if (!grid) return;

    if (!doctorList || doctorList.length === 0) {
        grid.innerHTML = `
            <div class="empty-state-box" style="grid-column: 1 / -1; text-align: center; padding: 3rem;">
                <i class="fa-solid fa-user-doctor" style="font-size: 3rem; color: #cbd5e1; margin-bottom: 1rem;"></i>
                <h3>No doctors found</h3>
                <p>Try adjusting your search or specialization filter.</p>
            </div>
        `;
        return;
    }

    grid.innerHTML = doctorList.map(doc => `
        <div class="doctor-card">
            <div class="doctor-card-top">
                <img src="${doc.photo}" alt="${doc.name}" class="doctor-photo" onerror="this.src='https://images.unsplash.com/photo-1622253692010-333f2da6031d?w=300'">
                <div class="doctor-info-head">
                    <h3 class="doc-name">${doc.name}</h3>
                    <span class="doc-spec">${doc.specialization}</span>
                    <span class="doc-hospital"><i class="fa-solid fa-hospital"></i> ${doc.hospital}</span>
                </div>
            </div>

            <div class="doctor-meta-pills">
                <div class="meta-pill">
                    <span class="meta-label">Rating</span>
                    <span class="meta-val rating-text">⭐ ${doc.rating} / 5</span>
                </div>
                <div class="meta-pill">
                    <span class="meta-label">Experience</span>
                    <span class="meta-val">${doc.experience} Years</span>
                </div>
                <div class="meta-pill">
                    <span class="meta-label">Fee</span>
                    <span class="meta-val">₹${doc.fee}</span>
                </div>
                <div class="meta-pill">
                    <span class="meta-label">Room</span>
                    <span class="meta-val">${doc.room_number}</span>
                </div>
            </div>

            <div class="token-available-bar">
                <span><i class="fa-solid fa-ticket"></i> Tokens Available:</span>
                <strong>${doc.available_tokens_count} Tokens</strong>
            </div>

            <div class="doctor-card-actions">
                <button class="btn btn-secondary" onclick="openDoctorModal(${doc.doctor_id})">VIEW DETAILS</button>
                <button class="btn btn-primary" onclick="openBookingModal(${doc.doctor_id})">BOOK TOKEN</button>
            </div>
        </div>
    `).join('');
}

function populateDoctorDropdowns() {
    const queueSelect = document.getElementById('queue-doctor-select');
    const adminSelect = document.getElementById('admin-doctor-select');

    if (!state.doctors.length) return;

    const optionsHTML = state.doctors.map(d => `<option value="${d.doctor_id}">${d.name} (${d.specialization} - ${d.hospital})</option>`).join('');

    if (queueSelect) {
        queueSelect.innerHTML = optionsHTML;
        queueSelect.value = state.currentQueueDoctorId;
    }
    if (adminSelect) {
        adminSelect.innerHTML = optionsHTML;
        adminSelect.value = state.adminDoctorId;
    }
}

// ==================== DOCTOR DETAILS & BOOKING MODALS ====================

async function openDoctorModal(doctorId) {
    try {
        const response = await fetch(`/api/doctors/${doctorId}`);
        const data = await response.json();
        if (data.success) {
            const doc = data.doctor;
            const modalBody = document.getElementById('doctor-modal-body');
            modalBody.innerHTML = `
                <div class="doc-detail-view">
                    <div style="display:flex; gap:1.5rem; align-items:center; margin-bottom:1.5rem;">
                        <img src="${doc.photo}" style="width:100px; height:100px; border-radius:12px; object-fit:cover;">
                        <div>
                            <h2>${doc.name}</h2>
                            <p style="color:var(--primary); font-weight:700;">${doc.specialization}</p>
                            <p style="color:var(--text-secondary);"><i class="fa-solid fa-hospital"></i> ${doc.hospital} (${doc.room_number})</p>
                        </div>
                    </div>
                    <p style="margin-bottom:1.5rem; font-size:0.95rem; color:var(--text-secondary);">${doc.bio}</p>

                    <div class="doctor-meta-pills" style="margin-bottom:1.5rem; grid-template-columns: repeat(3, 1fr);">
                        <div class="meta-pill"><span class="meta-label">Rating</span><span class="meta-val rating-text">⭐ ${doc.rating}</span></div>
                        <div class="meta-pill"><span class="meta-label">Experience</span><span class="meta-val">${doc.experience} Yrs</span></div>
                        <div class="meta-pill"><span class="meta-label">Consultation Fee</span><span class="meta-val">₹${doc.fee}</span></div>
                    </div>

                    <div style="background:#f8fafc; padding:1rem; border-radius:8px; margin-bottom:1.5rem; border:1px solid var(--border-color);">
                        <p><strong>Consultation Hours:</strong> ${doc.consultation_time}</p>
                        <p><strong>Current Active Token:</strong> Token ${doc.current_token || 'N/A'}</p>
                        <p><strong>Available Tokens Range:</strong> ${doc.token_range}</p>
                    </div>

                    <button class="btn btn-primary btn-large" style="width:100%;" onclick="closeDoctorModal(); openBookingModal(${doc.doctor_id});">
                        <i class="fa-solid fa-ticket"></i> BOOK CONSULTATION TOKEN
                    </button>
                </div>
            `;
            document.getElementById('doctor-details-modal').style.display = 'flex';
        }
    } catch (err) {
        console.error("Failed to load doctor details:", err);
    }
}

function closeDoctorModal() {
    document.getElementById('doctor-details-modal').style.display = 'none';
}

async function openBookingModal(doctorId) {
    try {
        const response = await fetch(`/api/doctors/${doctorId}`);
        const data = await response.json();
        if (data.success) {
            const doc = data.doctor;
            document.getElementById('booking-doctor-id').value = doc.doctor_id;
            document.getElementById('book-doc-name').textContent = doc.name;
            document.getElementById('book-doc-spec').textContent = doc.specialization;
            document.getElementById('book-doc-hospital').textContent = doc.hospital;
            document.getElementById('book-available-range').textContent = doc.token_range;

            document.getElementById('booking-modal').style.display = 'flex';
        }
    } catch (err) {
        console.error("Error setting up booking modal:", err);
    }
}

function closeBookingModal() {
    document.getElementById('booking-modal').style.display = 'none';
}

async function handleTokenBooking(event) {
    event.preventDefault();
    const doctorId = document.getElementById('booking-doctor-id').value;
    const patientName = document.getElementById('book-patient-name').value;
    const bookingDate = document.getElementById('book-date').value;
    const session = document.getElementById('book-session').value;

    try {
        const response = await fetch('/api/book-token', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: state.currentUserId,
                patient_name: patientName,
                doctor_id: parseInt(doctorId),
                booking_date: bookingDate,
                session: session
            })
        });

        const data = await response.json();
        if (data.success) {
            closeBookingModal();
            showBookingConfirmation(data.booking);
            loadMyTokens();
        }
    } catch (err) {
        console.error("Token booking failed:", err);
    }
}

function showBookingConfirmation(booking) {
    const cardContainer = document.getElementById('confirmation-token-card');
    if (cardContainer) {
        cardContainer.innerHTML = `
            <div style="display:flex; justify-content:space-between; margin-bottom:0.8rem; border-bottom:1px solid #cbd5e1; padding-bottom:0.5rem;">
                <strong>Booking Ref: ${booking.booking_ref}</strong>
                <span class="token-status-badge waiting">${booking.status}</span>
            </div>
            <p><strong>Doctor:</strong> ${booking.doctor_name}</p>
            <p><strong>Department:</strong> ${booking.specialization}</p>
            <p><strong>Hospital:</strong> ${booking.hospital} (${booking.room_number})</p>
            <p><strong>Date:</strong> ${booking.booking_date} (${booking.session})</p>
            <hr style="margin:0.8rem 0; border:none; border-top:1px dashed #cbd5e1;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <span style="font-size:0.8rem; text-transform:uppercase; color:var(--text-secondary);">Your Digital Token</span>
                    <h2 style="font-size:2.8rem; font-weight:900; color:var(--primary); line-height:1;">TOKEN ${booking.token_number}</h2>
                </div>
                <div style="text-align:right;">
                    <span style="font-size:0.8rem; color:var(--text-secondary);">Estimated Time</span>
                    <h3 style="font-size:1.3rem; font-weight:800; color:var(--text-primary);">${booking.estimated_consultation_time}</h3>
                </div>
            </div>
        `;
    }

    state.currentQueueDoctorId = booking.doctor_id;
    document.getElementById('confirmation-modal').style.display = 'flex';
}

function closeConfirmationModal() {
    document.getElementById('confirmation-modal').style.display = 'none';
}

function goToQueueFromConfirmation() {
    closeConfirmationModal();
    navigateTo('queue-status');
}

// ==================== MY TOKENS PAGE ====================

async function loadMyTokens() {
    try {
        const response = await fetch(`/api/my-tokens?user_id=${state.currentUserId}`);
        const data = await response.json();

        if (data.success) {
            state.activeUserBookings = data.bookings;
            renderMyTokens(data.bookings);
            
            const badge = document.getElementById('nav-token-badge');
            if (badge) {
                badge.textContent = data.bookings.length;
                badge.style.display = data.bookings.length > 0 ? 'inline-block' : 'none';
            }
        }
    } catch (err) {
        console.error("Failed to load user tokens:", err);
    }
}

function renderMyTokens(bookings) {
    const container = document.getElementById('my-tokens-list-container');
    if (!container) return;

    if (!bookings || bookings.length === 0) {
        container.innerHTML = `
            <div style="text-align:center; padding:4rem; background:#ffffff; border-radius:16px; border:1px solid var(--border-color);">
                <i class="fa-solid fa-ticket-simple" style="font-size:3.5rem; color:#cbd5e1; margin-bottom:1rem;"></i>
                <h3>No active token bookings</h3>
                <p style="color:var(--text-secondary); margin-bottom:1.5rem;">Select your symptoms or find a doctor to book your first digital consultation token.</p>
                <button class="btn btn-primary" onclick="navigateTo('symptoms')">SELECT SYMPTOMS</button>
            </div>
        `;
        return;
    }

    container.innerHTML = bookings.map(b => {
        let notiHTML = '';
        if (b.token_number === b.current_token) {
            notiHTML = `
                <div class="notification-alert-card active-turn" style="margin-bottom:1rem;">
                    <div class="noti-icon"><i class="fa-solid fa-bell fa-bounce"></i></div>
                    <div class="noti-text">
                        <h4>YOUR CONSULTATION IS NOW IN PROGRESS!</h4>
                        <p>Token <strong>#${b.token_number}</strong> is currently being called. Please proceed directly to Room <strong>${b.room_number || '102'}</strong>.</p>
                    </div>
                </div>
            `;
        } else if (b.token_number > b.current_token && b.patients_ahead <= 3) {
            notiHTML = `
                <div class="notification-alert-card approaching-turn" style="margin-bottom:1rem;">
                    <div class="noti-icon"><i class="fa-solid fa-clock-rotate-left"></i></div>
                    <div class="noti-text">
                        <h4>YOUR CONSULTATION IS APPROACHING!</h4>
                        <p>Your turn is approaching with <strong>${b.patients_ahead} patient(s)</strong> ahead (~${b.estimated_wait_minutes} mins wait). Please be ready.</p>
                    </div>
                </div>
            `;
        }

        return `
        <div class="my-token-card">
            ${notiHTML}
            <div class="my-token-header">
                <div>
                    <span class="booking-ref-tag">${b.booking_ref}</span>
                    <h3 style="margin-top:0.3rem;">${b.doctor_name}</h3>
                    <p style="font-size:0.85rem; color:var(--text-secondary);">${b.specialization} • ${b.hospital}</p>
                </div>
                <span class="token-status-badge ${b.patients_ahead === 0 ? 'consulting' : 'waiting'}">
                    ${b.status}
                </span>
            </div>

            <div class="token-grid-stats">
                <div class="token-stat-box highlight-user">
                    <div class="stat-title">Your Token</div>
                    <div class="stat-value-huge" style="color:var(--primary);">${b.token_number}</div>
                </div>

                <div class="token-stat-box highlight-current">
                    <div class="stat-title">Current Token</div>
                    <div class="stat-value-huge" style="color:var(--secondary);">${b.current_token}</div>
                </div>

                <div class="token-stat-box">
                    <div class="stat-title">Patients Ahead</div>
                    <div class="stat-value-huge">${b.patients_ahead}</div>
                </div>

                <div class="token-stat-box">
                    <div class="stat-title">Est. Waiting Time</div>
                    <div class="stat-value-huge" style="font-size:1.8rem; margin-top:0.3rem;">${b.estimated_wait_minutes} Mins</div>
                    <span style="font-size:0.75rem; color:var(--text-secondary);">${b.estimated_consultation_time || ''}</span>
                </div>
            </div>

            <div style="display:flex; justify-content:flex-end;">
                <button class="btn btn-primary" onclick="state.currentQueueDoctorId=${b.doctor_id}; navigateTo('queue-status');">
                    <i class="fa-solid fa-wave-square"></i> TRACK LIVE QUEUE
                </button>
            </div>
        </div>
    `;
    }).join('');
}

// ==================== LIVE QUEUE TRACKER ====================

async function loadQueueData() {
    const select = document.getElementById('queue-doctor-select');
    if (select && select.value) {
        state.currentQueueDoctorId = parseInt(select.value);
    }

    try {
        const response = await fetch(`/api/queue/${state.currentQueueDoctorId}`);
        const data = await response.json();

        if (data.success) {
            renderQueueDashboard(data);
        }
    } catch (err) {
        console.error("Failed to load queue tracker:", err);
    }
}

function renderQueueDashboard(data) {
    const container = document.getElementById('queue-details-display');
    if (!container) return;

    const doc = data.doctor;
    const currentTok = data.current_token;

    // Check if current user has a token for this doctor
    const userBooking = state.activeUserBookings.find(b => b.doctor_id === doc.doctor_id);
    const userTokenNum = userBooking ? userBooking.token_number : 31; // Default demonstration token if none booked

    const patientsAhead = Math.max(0, userTokenNum - currentTok - 1);
    const waitTimeMins = patientsAhead * data.avg_consultation_time;

    const timelineHTML = data.timeline.map(item => {
        let rowClass = "";
        let badgeText = item.status;

        if (item.is_current) {
            rowClass = "consulting";
            badgeText = "CURRENTLY CONSULTING";
        } else if (item.token_number === userTokenNum) {
            rowClass = "user-token";
            badgeText = "YOU (YOUR TOKEN)";
        }

        return `
            <div class="timeline-row ${rowClass}">
                <div style="display:flex; align-items:center; gap:1rem;">
                    <strong style="font-size:1.1rem;">TOKEN ${item.token_number}</strong>
                    <span>${item.patient_name}</span>
                </div>
                <span style="font-size:0.8rem; text-transform:uppercase;">${badgeText}</span>
            </div>
        `;
    }).join('');

    // Generate Notification Alert HTML if active booking exists or demo token
    let notificationBannerHTML = '';
    if (currentTok === userTokenNum) {
        notificationBannerHTML = `
            <div class="notification-alert-card active-turn">
                <div class="noti-icon"><i class="fa-solid fa-bell fa-bounce"></i></div>
                <div class="noti-text">
                    <h4>YOUR CONSULTATION IS NOW IN PROGRESS!</h4>
                    <p>Token <strong>#${userTokenNum}</strong> is currently being called by ${doc.name}. Please proceed directly to <strong>Room ${doc.room_number}</strong>.</p>
                </div>
            </div>
        `;
    } else if (userTokenNum > currentTok && patientsAhead <= 3) {
        notificationBannerHTML = `
            <div class="notification-alert-card approaching-turn">
                <div class="noti-icon"><i class="fa-solid fa-clock-rotate-left"></i></div>
                <div class="noti-text">
                    <h4>YOUR CONSULTATION IS APPROACHING!</h4>
                    <p>Your Token: <strong>${userTokenNum}</strong> | Current Token: <strong>${currentTok}</strong> | <strong>${patientsAhead} patient${patientsAhead > 1 ? 's' : ''}</strong> ahead (${waitTimeMins} mins wait).</p>
                    <p>Please be ready and present near <strong>Room ${doc.room_number}</strong>.</p>
                </div>
            </div>
        `;
    }

    container.innerHTML = `
        ${notificationBannerHTML}
        <div class="live-hero-queue-box">
            <div>
                <h3 style="font-size:1.4rem; font-weight:800; color:var(--text-primary);">${doc.name}</h3>
                <p style="color:var(--primary); font-weight:700;">${doc.specialization} • ${doc.hospital}</p>
                <p style="font-size:0.85rem; color:var(--text-secondary); margin-top:0.3rem;"><i class="fa-solid fa-door-open"></i> Room ${doc.room_number} | Session: ${doc.consultation_time}</p>
            </div>

            <div class="currently-consulting-badge">
                <span class="consulting-label">CURRENTLY CONSULTING</span>
                <div class="token-big-num">TOKEN ${currentTok}</div>
                <span style="font-size:0.75rem; color:var(--success); font-weight:700;"><i class="fa-solid fa-sync fa-spin"></i> Live Consultation in Progress</span>
            </div>
        </div>

        <div class="queue-calc-summary">
            <div class="calc-box your-token-box">
                <div class="stat-title">YOUR TOKEN</div>
                <div style="font-size:2rem; font-weight:800; color:var(--primary);">TOKEN ${userTokenNum}</div>
                <span style="font-size:0.75rem; color:var(--primary); font-weight:700;">${userBooking ? 'Booked Appointment' : 'Sample Demonstration'}</span>
            </div>

            <div class="calc-box">
                <div class="stat-title">PATIENTS AHEAD</div>
                <div style="font-size:2rem; font-weight:800;">${patientsAhead}</div>
                <span style="font-size:0.75rem; color:var(--text-secondary);">${userTokenNum} - ${currentTok} - 1</span>
            </div>

            <div class="calc-box">
                <div class="stat-title">ESTIMATED WAITING</div>
                <div style="font-size:2rem; font-weight:800; color:var(--warning);">${waitTimeMins} Mins</div>
                <span style="font-size:0.75rem; color:var(--text-secondary);">${patientsAhead} patients × ${data.avg_consultation_time} mins</span>
            </div>
        </div>

        <div class="queue-timeline-container">
            <div class="timeline-title">
                <i class="fa-solid fa-list-ol"></i> Live Consultation Queue Breakdown Timeline
            </div>
            <div class="timeline-list">
                ${timelineHTML}
            </div>
        </div>
    `;
}

function startQueuePolling() {
    stopQueuePolling();
    state.queuePollInterval = setInterval(() => {
        if (state.activePage === 'queue-status') {
            loadQueueData();
        }
    }, 5000); // 5 seconds real-time auto-refresh
}

function stopQueuePolling() {
    if (state.queuePollInterval) {
        clearInterval(state.queuePollInterval);
        state.queuePollInterval = null;
    }
}

// ==================== DOCTOR / RECEPTIONIST ADMIN DESK ====================

async function loadAdminQueueData() {
    const select = document.getElementById('admin-doctor-select');
    if (select && select.value) {
        state.adminDoctorId = parseInt(select.value);
    }

    try {
        const response = await fetch(`/api/queue/${state.adminDoctorId}`);
        const data = await response.json();
        if (data.success) {
            renderAdminDashboard(data);
        }
    } catch (err) {
        console.error("Failed to load admin queue:", err);
    }
}

function renderAdminDashboard(data) {
    const container = document.getElementById('admin-queue-view');
    if (!container) return;

    const currentTok = data.current_token;
    const doc = data.doctor;

    container.innerHTML = `
        <div class="admin-controls-dashboard">
            <div class="desk-live-box">
                <span class="stat-title">CURRENT CONSULTING TOKEN</span>
                <div class="desk-token-num">TOKEN ${currentTok}</div>
                <p style="color:var(--text-secondary); font-size:0.9rem; margin-top:0.5rem;">
                    Doctor: <strong>${doc.name}</strong> (${doc.specialization})
                </p>

                <div class="admin-buttons-flex">
                    <button class="btn btn-secondary" onclick="adminPrevToken(${doc.doctor_id})">
                        <i class="fa-solid fa-chevron-left"></i> PREVIOUS TOKEN
                    </button>
                    <button class="btn btn-success btn-large" onclick="adminNextToken(${doc.doctor_id})">
                        <i class="fa-solid fa-bullhorn"></i> CALL NEXT TOKEN
                    </button>
                </div>
            </div>

            <div style="background:#ffffff; border:1px solid var(--border-color); border-radius:12px; padding:1.5rem;">
                <h4 style="margin-bottom:1rem;"><i class="fa-solid fa-user-clock"></i> Waiting Patients Queue</h4>
                <div style="max-height:300px; overflow-y:auto; display:flex; flex-direction:column; gap:0.5rem;">
                    ${data.timeline.filter(t => t.token_number >= currentTok).map(t => `
                        <div style="display:flex; justify-content:space-between; padding:0.6rem 0.8rem; background:#f8fafc; border-radius:6px; border:1px solid #e2e8f0; font-size:0.88rem;">
                            <strong>Token ${t.token_number}</strong>
                            <span>${t.patient_name}</span>
                            <span style="color:${t.is_current ? 'var(--success)' : 'var(--text-secondary)'}; font-weight:700;">${t.status}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
}

async function adminNextToken(doctorId) {
    try {
        const response = await fetch(`/api/queue/${doctorId}/next`, { method: 'POST' });
        const data = await response.json();
        if (data.success) {
            loadAdminQueueData();
            loadMyTokens(); // refresh user tokens
        }
    } catch (err) {
        console.error("Error advancing queue:", err);
    }
}

async function adminPrevToken(doctorId) {
    try {
        const response = await fetch(`/api/queue/${doctorId}/prev`, { method: 'POST' });
        const data = await response.json();
        if (data.success) {
            loadAdminQueueData();
            loadMyTokens();
        }
    } catch (err) {
        console.error("Error stepping back queue:", err);
    }
}

function setupEventListeners() {
    // Setup modal close events on overlay click
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                overlay.style.display = 'none';
            }
        });
    });
}
