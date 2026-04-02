function viewDetails(id) {
    const ver = verificationData.find(v => v.id === id);
    if (!ver) {
        showNotification('Verification case not found.', 'error');
        return;
    }
    
    const doc = documentData.find(d => d.verification_id === id);
    let extractedText = doc ? (doc.extracted_text || "") : "";
    if (!extractedText.trim()) {
        extractedText = `Name: ${ver.name}\nDOB: 01/01/1990\nAddress: 123 Reviewer St, City\nID: 9999-9999-9999`;
    }
    
    // Extract pieces
    const nameMatch = extractedText.match(/Name:\s*([^\n]+)/i);
    const dobMatch = extractedText.match(/DOB:\s*([^\n]+)/i) || extractedText.match(/Date of Birth:\s*([^\n]+)/i) || extractedText.match(/(?:(?:0[1-9]|[12]\d|3[01])\/(?:0[1-9]|1[0-2])\/(?:19|20)\d{2})/);
    const dName = nameMatch ? nameMatch[1] : ver.name;
    const dDOB = dobMatch ? (dobMatch[1] || dobMatch[0]) : "11 NOV 90";
    const dDocType = ver.docType || "Passport";
    
    const isFaceMatch = ver.confidence >= 0.70;
    const initials = dName.split(' ').map(n=>n[0]).join('').substring(0,2).toUpperCase();

    // Create the overlay container
    const overlay = document.createElement('div');
    overlay.className = 'case-review-overlay';
    // Base styles for the backdrop
    overlay.style.cssText = `
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: rgba(0,0,0,0.6); backdrop-filter: blur(5px);
        display: flex; justify-content: center; align-items: center; z-index: 99999;
        font-family: 'Inter', sans-serif;
    `;
    
    // SVG Document Graphic to act as realistic placeholder
    const mapPlaceholderSVG = `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='500' height='320' viewBox='0 0 500 320'%3E%3Crect width='500' height='320' fill='%23e0dac8' rx='10'/%3E%3Ctext x='40' y='50' font-family='Arial' font-size='16' font-weight='bold' fill='%23333'%3EPASSPORT%3C/text%3E%3Crect x='40' y='90' width='100' height='120' fill='%23666'/%3E%3Ctext x='160' y='95' font-family='monospace' font-size='11' fill='%23555'%3ESurname%3C/text%3E%3Ctext x='160' y='115' font-family='monospace' font-size='18' font-weight='bold' fill='%23111'%3E${(dName.split(' ').pop() || 'DOE').toUpperCase()}%3C/text%3E%3Ctext x='160' y='140' font-family='monospace' font-size='11' fill='%23555'%3EGiven name%3C/text%3E%3Ctext x='160' y='160' font-family='monospace' font-size='18' font-weight='bold' fill='%23111'%3E${(dName.split(' ')[0] || 'JOHN').toUpperCase()}%3C/text%3E%3Ctext x='160' y='185' font-family='monospace' font-size='11' fill='%23555'%3EDate of birth%3C/text%3E%3Ctext x='160' y='205' font-family='monospace' font-size='14' font-weight='bold' fill='%23111'%3E${dDOB}%3C/text%3E%3Ctext x='40' y='270' font-family='monospace' font-size='18' letter-spacing='2' fill='%23111'%3EP%3CUSA${(dName.split(' ').pop() || 'DOE').toUpperCase()}%3C%3C${(dName.split(' ')[0] || 'JOHN').toUpperCase()}%3C%3C%3C%3C%3C%3C%3C%3C%3C%3C%3C%3C%3C%3C%3C%3C%3C/text%3E%3Ctext x='40' y='295' font-family='monospace' font-size='18' letter-spacing='2' fill='%23111'%3E1234567890USA901111M310119121234567890%3C/text%3E%3C/svg%3E")`;

    const content = `
        <div style="background:#fff; width:95%; max-width:1300px; height:85vh; border-radius:12px; overflow:hidden; display:flex; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);">
            
            <!-- Left Column: User Context & AI Checks -->
            <div style="width: 300px; border-right: 1px solid #e5e7eb; display:flex; flex-direction:column; background:#ffffff; flex-shrink:0;">
                <div style="padding: 24px; border-bottom: 1px solid #f3f4f6;">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:12px;">
                        <h2 style="margin:0; font-size:1.25rem; font-weight:600; color:#111827;">${dName}</h2>
                        <div style="width:40px; height:40px; border-radius:50%; background:#f3f4f6; display:flex; align-items:center; justify-content:center; font-weight:600; color:#374151; font-size:0.875rem; position:relative;">
                            ${initials}
                            <span style="position:absolute; bottom:0; right:0; width:10px; height:10px; background:#10b981; border:2px solid white; border-radius:50%;"></span>
                        </div>
                    </div>
                    <div style="display:flex; gap:8px; margin-bottom:24px;">
                        <span style="background:#ecfdf5; color:#059669; padding:4px 8px; border-radius:4px; font-size:0.75rem; font-weight:500;">Customer</span>
                        <span style="background:#f3f4f6; color:#4b5563; padding:4px 8px; border-radius:4px; font-size:0.75rem;">Uploaded today</span>
                    </div>

                    <div style="display:flex; flex-direction:column; gap:12px; font-size:0.875rem;">
                        <div style="display:flex; justify-content:space-between; text-align:right;">
                            <span style="color:#6b7280;">Email</span>
                            <span style="color:#0ea5e9;">${ver.email}</span>
                        </div>
                        <div style="display:flex; justify-content:space-between;">
                            <span style="color:#6b7280;">Phone</span>
                            <span style="color:#0ea5e9;">+1 (555) 000-0000</span>
                        </div>
                        <div style="display:flex; justify-content:space-between;">
                            <span style="color:#6b7280;">Company</span>
                            <span style="color:#0ea5e9;">Citadel Ltd</span>
                        </div>
                    </div>
                </div>

                <div style="padding: 24px; flex:1; overflow-y:auto; background:#fafafa;">
                    <div style="margin-bottom:15px; display:flex; font-size:0.875rem;">
                        <span style="color:#0ea5e9; font-weight:500; border:1px solid #bae6fd; padding:6px 12px; border-radius:16px;">Applicant</span>
                    </div>
                    <div style="background:#fff; border:1px solid ${isFaceMatch ? '#d1fae5' : '#fee2e2'}; border-radius:8px; overflow:hidden;">
                        <div style="padding:12px 16px; border-bottom:1px solid #f3f4f6; display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-weight:600; color:#374151; font-size:0.875rem;">${dDocType}</span>
                            <span style="color:${isFaceMatch ? '#059669' : '#ef4444'}; font-size:0.75rem; font-weight:500;">${isFaceMatch ? 'Valid' : 'AI found issues'}</span>
                        </div>
                        <div style="padding:0;">
                            <div style="padding:12px 16px; border-bottom:1px solid #f3f4f6; display:flex; justify-content:space-between; align-items:center;">
                                <span style="font-size:0.875rem; color:#4b5563; width:70%;">Was applicant born after min DATE?</span>
                                <span style="background:#f3f4f6; padding:4px 8px; border-radius:16px; font-size:0.75rem; font-weight:600; color:#374151;">Yes</span>
                            </div>
                            <div style="padding:12px 16px; border-bottom:1px solid #f3f4f6; display:flex; justify-content:space-between; align-items:center;">
                                <span style="font-size:0.875rem; color:#4b5563; width:70%;">The date matches your application</span>
                                <span style="background:#f3f4f6; padding:4px 8px; border-radius:16px; font-size:0.75rem; font-weight:600; color:#374151;">Yes</span>
                            </div>
                            <div style="padding:12px 16px; border-bottom:1px solid #f3f4f6; display:flex; justify-content:space-between; align-items:center;">
                                <span style="font-size:0.875rem; color:#4b5563; width:70%;">Valid ID document identified?</span>
                                <span style="background:#f3f4f6; padding:4px 8px; border-radius:16px; font-size:0.75rem; font-weight:600; color:#374151;">Yes</span>
                            </div>
                            <div style="padding:12px 16px; display:flex; justify-content:space-between; align-items:center; background:${isFaceMatch ? 'transparent':'#fef2f2'};">
                                <span style="font-size:0.875rem; color:#4b5563; width:70%;">Face match confirmed against selfie?</span>
                                <span style="background:${isFaceMatch ? '#f3f4f6' : '#fee2e2'}; padding:4px 8px; border-radius:16px; font-size:0.75rem; font-weight:600; color:${isFaceMatch ? '#374151' : '#dc2626'};">${isFaceMatch ? 'Yes' : 'No'}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Middle Column: Document Viewer -->
            <div style="flex:1; background:#f9fafb; position:relative; display:flex; flex-direction:column; align-items:center; padding:24px;">
                <div style="width:100%; display:flex; justify-content:center; margin-bottom:40px;">
                    <span style="color:#6b7280; font-size:0.875rem; font-weight:500;">Viewing ${dName.split(' ')[0]}'s ${dDocType}</span>
                </div>
                
                <!-- Mock Image Viewer -->
                <div style="width: 500px; height: 320px; background-color: #e0dac8; background-image: ${mapPlaceholderSVG}; background-size: cover; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06); position:relative;">
                </div>

                <div style="position:absolute; bottom:24px; left:24px; display:flex; flex-direction:column; gap:8px;">
                    <button style="width:36px; height:36px; background:#fff; border:1px solid #e5e7eb; border-radius:8px; display:flex; align-items:center; justify-content:center; cursor:pointer; color:#374151; font-size:1.2rem; box-shadow:0 1px 2px rgba(0,0,0,0.05);">+</button>
                    <button style="width:36px; height:36px; background:#fff; border:1px solid #e5e7eb; border-radius:8px; display:flex; align-items:center; justify-content:center; cursor:pointer; color:#374151; font-size:1.2rem; box-shadow:0 1px 2px rgba(0,0,0,0.05);">-</button>
                </div>
            </div>

            <!-- Right Column: Task Workflow -->
            <div style="width: 340px; background:#ffffff; border-left: 1px solid #e5e7eb; display:flex; flex-direction:column; flex-shrink:0;">
                <div style="padding:24px; display:flex; justify-content:flex-end;">
                    <button onclick="this.closest('.case-review-overlay').remove()" style="background:transparent; border:none; font-size:1.5rem; cursor:pointer; color:#9ca3af; outline:none;">?</button>
                </div>
                
                <div style="padding: 0 32px 32px 32px; flex:1; overflow-y:auto;">
                    <div style="width:40px; height:40px; background:#0d9488; border-radius:8px; display:flex; align-items:center; justify-content:center; margin-bottom:24px;">
                        <span style="color:white; font-size:1.2rem;">?</span>
                    </div>

                    <p style="color:#6b7280; font-size:0.75rem; text-transform:uppercase; font-weight:600; margin:0 0 8px 0; letter-spacing:0.05em;">Current Task</p>
                    <h2 style="font-size:1.125rem; color:#111827; margin:0 0 24px 0; line-height:1.5; font-weight:600;">
                        Review the ${dName} ${dDocType} Application and all supporting documents to ensure accuracy and completeness.
                    </h2>

                    <button onclick="alert('Review process completed! Status updated.'); this.closest('.case-review-overlay').remove();" style="width:100%; background:#0d9488; color:white; border:none; padding:12px; border-radius:6px; font-weight:500; cursor:pointer; margin-bottom:32px; transition:background 0.2s;">
                        Start application review
                    </button>

                    <!-- Vertical Stepper -->
                    <div style="position:relative; padding-left:12px;">
                        <div style="position:absolute; left:23px; top:12px; bottom:20px; width:2px; background:#e5e7eb;"></div>
                        
                        <div style="display:flex; align-items:flex-start; gap:16px; margin-bottom:32px; position:relative; z-index:1;">
                            <div style="width:24px; height:24px; background:#111827; color:white; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:0.75rem; font-weight:600; flex-shrink:0;">1</div>
                            <div style="padding-top:2px;">
                                <p style="margin:0 0 8px 0; font-size:0.875rem; font-weight:500; color:#111827;">Start application to see next steps</p>
                                <div style="height:6px; width:120px; background:#e5e7eb; border-radius:3px;"></div>
                            </div>
                        </div>

                        <div style="display:flex; align-items:flex-start; gap:16px; margin-bottom:32px; position:relative; z-index:1; opacity:0.5;">
                            <div style="width:24px; height:24px; background:#fff; color:#9ca3af; border:2px solid #e5e7eb; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:0.75rem; font-weight:600; flex-shrink:0;">2</div>
                            <div style="padding-top:2px;">
                                <p style="margin:0 0 8px 0; font-size:0.875rem; font-weight:500; color:#374151;">Verify Data Elements</p>
                                <div style="height:6px; width:160px; background:#e5e7eb; border-radius:3px;"></div>
                            </div>
                        </div>

                        <div style="display:flex; align-items:flex-start; gap:16px; margin-bottom:32px; position:relative; z-index:1; opacity:0.5;">
                            <div style="width:24px; height:24px; background:#fff; color:#9ca3af; border:2px solid #e5e7eb; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:0.75rem; font-weight:600; flex-shrink:0;">3</div>
                            <div style="padding-top:2px;">
                                <p style="margin:0 0 8px 0; font-size:0.875rem; font-weight:500; color:#374151;">Contact customer</p>
                                <div style="height:6px; width:100px; background:#e5e7eb; border-radius:3px;"></div>
                            </div>
                        </div>

                        <div style="display:flex; align-items:flex-start; gap:16px; position:relative; z-index:1; opacity:0.5;">
                            <div style="width:24px; height:24px; background:#fff; color:#9ca3af; border:2px solid #e5e7eb; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:0.75rem; font-weight:600; flex-shrink:0;">4</div>
                            <div style="padding-top:2px;">
                                <p style="margin:0 0 8px 0; font-size:0.875rem; font-weight:500; color:#374151;">Complete Verification</p>
                                <div style="height:6px; width:130px; background:#e5e7eb; border-radius:3px;"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    overlay.innerHTML = content;
    document.body.appendChild(overlay);
}
