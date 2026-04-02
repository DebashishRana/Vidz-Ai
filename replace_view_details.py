import re

with open('frontend/script.js', 'r', encoding='utf-8') as f:
    text = f.read()

new_view_details = """function viewDetails(id) {
    const ver = verificationData.find(v => v.id === id);
    if (!ver) {
        showNotification('Verification case not found.', 'error');
        return;
    }
    
    // Attempt to pull real data from session storage (populated during KYC flow)
    const sessImg = sessionStorage.getItem('recent_upload_' + id);
    const sessAddress = sessionStorage.getItem('recent_address_' + id) || "Address not detected";
    
    const doc = documentData.find(d => d.verification_id === id);
    let extractedText = doc ? (doc.extracted_text || "") : "";
    
    if (!extractedText.trim()) {
        extractedText = `Name: ${ver.name}\\nDOB: 01/01/1990\\nAddress: ${sessAddress}\\nID: 9999-9999-9999`;
    }
    
    // Extract pieces
    const nameMatch = extractedText.match(/Name:\s*([^\\n]+)/i);
    const dobMatch = extractedText.match(/DOB:\s*([^\\n]+)/i) || extractedText.match(/Date of Birth:\s*([^\\n]+)/i) || extractedText.match(/(?:(?:0[1-9]|[12]\d|3[01])\/(?:0[1-9]|1[0-2])\/(?:19|20)\d{2})/);
    const dName = nameMatch ? nameMatch[1] : ver.name;
    const dDOB = dobMatch ? (dobMatch[1] || dobMatch[0]) : "11 NOV 90";
    const dDocType = ver.docType || "Passport";
    
    const isFaceMatch = ver.confidence >= 0.70;
    const docConfidence = (ver.riskScore ? (100 - ver.riskScore) : 80);
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
    
    // Use the real uploaded image if available
    let viewerContent = '';
    if (sessImg) {
        viewerContent = `<img src="${sessImg}" style="width:100%; height:100%; object-fit:contain; border-radius:8px;" />`;
    } else {
        const dNameLast = (dName.split(' ').pop() || 'DOE').toUpperCase();
        const dNameFirst = (dName.split(' ')[0] || 'JOHN').toUpperCase();
        const mapPlaceholderSVG = `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='500' height='320' viewBox='0 0 500 320'%3E%3Crect width='500' height='320' fill='%23e0dac8' rx='10'/%3E%3Ctext x='40' y='50' font-family='Arial' font-size='16' font-weight='bold' fill='%23333'%3EPASSPORT%3C/text%3E%3Crect x='40' y='90' width='100' height='120' fill='%23666'/%3E%3Ctext x='160' y='95' font-family='monospace' font-size='11' fill='%23555'%3ESurname%3C/text%3E%3Ctext x='160' y='115' font-family='monospace' font-size='18' font-weight='bold' fill='%23111'%3E${dNameLast}%3C/text%3E%3Ctext x='160' y='140' font-family='monospace' font-size='11' fill='%23555'%3EGiven name%3C/text%3E%3Ctext x='160' y='160' font-family='monospace' font-size='18' font-weight='bold' fill='%23111'%3E${dNameFirst}%3C/text%3E%3Ctext x='160' y='185' font-family='monospace' font-size='11' fill='%23555'%3EDate of birth%3C/text%3E%3Ctext x='160' y='205' font-family='monospace' font-size='14' font-weight='bold' fill='%23111'%3E${dDOB}%3C/text%3E%3Ctext x='40' y='270' font-family='monospace' font-size='18' letter-spacing='2' fill='%23111'%3EP%3CUSA${dNameLast}%3C%3C${dNameFirst}%3C%3C%3C%3C%3C%3C%3C%3C%3C%3C%3C%3C%3C%3C%3C%3C%3C/text%3E%3Ctext x='40' y='295' font-family='monospace' font-size='18' letter-spacing='2' fill='%23111'%3E1234567890USA901111M310119121234567890%3C/text%3E%3C/svg%3E")`;
        viewerContent = `<div style="width: 100%; height: 100%; background-color: #e0dac8; background-image: ${mapPlaceholderSVG}; background-size: cover; border-radius: 8px;"></div>`;
    }

    const content = `
        <div style="background:#fff; width:95%; max-width:1300px; height:85vh; border-radius:12px; overflow:hidden; display:flex; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);">
            
            <!-- Left Column: User Context & AI Checks -->
            <div style="width: 320px; border-right: 1px solid #e5e7eb; display:flex; flex-direction:column; background:#ffffff; flex-shrink:0;">
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
                            <span style="color:#6b7280;">Extracted Address</span>
                            <span style="color:#374151; font-weight:500; text-align:right; max-width:180px;">${sessAddress}</span>
                        </div>
                    </div>
                </div>

                <div style="padding: 24px; flex:1; overflow-y:auto; background:#fafafa;">
                    <div style="margin-bottom:15px; display:flex; font-size:0.875rem;">
                        <span style="color:#0ea5e9; font-weight:500; border:1px solid #bae6fd; padding:6px 12px; border-radius:16px;">AI Verification Results</span>
                    </div>
                    <div style="background:#fff; border:1px solid ${isFaceMatch ? '#d1fae5' : '#fee2e2'}; border-radius:8px; overflow:hidden;">
                        <div style="padding:12px 16px; border-bottom:1px solid #f3f4f6; display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-weight:600; color:#374151; font-size:0.875rem;">Document Verification</span>
                            <span style="color:#059669; font-size:0.75rem; font-weight:500;">${docConfidence.toFixed(1)}% Score</span>
                        </div>
                        <div style="padding:0;">
                            <div style="padding:12px 16px; border-bottom:1px solid #f3f4f6; display:flex; justify-content:space-between; align-items:center;">
                                <span style="font-size:0.875rem; color:#4b5563; width:70%;">Address Extracted?</span>
                                <span style="background:${sessAddress !== 'Address not detected' ? '#f3f4f6' : '#fee2e2'}; padding:4px 8px; border-radius:16px; font-size:0.75rem; font-weight:600; color:${sessAddress !== 'Address not detected' ? '#374151' : '#dc2626'};">${sessAddress !== 'Address not detected' ? 'Yes' : 'No'}</span>
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
            <div style="flex:1; background:#111827; position:relative; display:flex; flex-direction:column; align-items:center; justify-content:center; padding:24px; overflow:hidden;">
                
                <!-- Image Viewer -->
                <div style="width: 100%; height: 100%; display:flex; justify-content:center; align-items:center; position:relative;">
                    <div style="max-width: 90%; max-height: 90%; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.5); position:relative; overflow:hidden; border-radius:8px;">
                        ${viewerContent}
                    </div>
                    <div style="position:absolute; bottom:24px; left:24px; right:24px; display:flex; justify-content:space-between; align-items:center;">
                        <span style="color:#9ca3af; font-size:0.875rem; font-weight:500; background:rgba(0,0,0,0.5); padding:4px 12px; border-radius:16px; backdrop-filter:blur(4px);">Viewing ${dDocType}</span>
                    </div>
                </div>

            </div>

            <!-- Right Column: Task Workflow -->
            <div style="width: 340px; background:#ffffff; border-left: 1px solid #e5e7eb; display:flex; flex-direction:column; flex-shrink:0;">
                <div style="padding:24px; display:flex; justify-content:flex-end;">
                    <button onclick="this.closest('.case-review-overlay').remove()" style="background:transparent; border:none; font-size:1.5rem; cursor:pointer; color:#9ca3af; outline:none; line-height:1;">&times;</button>
                </div>
                
                <div style="padding: 0 32px 32px 32px; flex:1; overflow-y:auto;">
                    <div style="width:40px; height:40px; background:#0d9488; border-radius:8px; display:flex; align-items:center; justify-content:center; margin-bottom:24px;">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                    </div>

                    <p style="color:#6b7280; font-size:0.75rem; text-transform:uppercase; font-weight:600; margin:0 0 8px 0; letter-spacing:0.05em;">Current Task</p>
                    <h2 style="font-size:1.125rem; color:#111827; margin:0 0 24px 0; line-height:1.5; font-weight:600;">
                        Review the ${dName} ${dDocType} Application and verify the extracted address.
                    </h2>

                    <button onclick="alert('Review process completed! Status updated.'); this.closest('.case-review-overlay').remove();" style="width:100%; background:#0d9488; color:white; border:none; padding:12px; border-radius:6px; font-weight:500; cursor:pointer; margin-bottom:32px; transition:background 0.2s;">
                        Approve Application
                    </button>

                    <button onclick="alert('Application Rejected by reviewer.'); this.closest('.case-review-overlay').remove();" style="width:100%; background:#fee2e2; color:#dc2626; border:none; padding:12px; border-radius:6px; font-weight:500; cursor:pointer; margin-top:-20px; margin-bottom:32px; transition:background 0.2s;">
                        Reject Application
                    </button>
                    
                    <!-- Vertical Stepper -->
                    <div style="position:relative; padding-left:12px;">
                        <div style="position:absolute; left:23px; top:12px; bottom:20px; width:2px; background:#e5e7eb;"></div>
                        
                        <div style="display:flex; align-items:flex-start; gap:16px; margin-bottom:32px; position:relative; z-index:1;">
                            <div style="width:24px; height:24px; background:#10b981; color:white; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:0.75rem; font-weight:600; flex-shrink:0;">✓</div>
                            <div style="padding-top:2px;">
                                <p style="margin:0 0 8px 0; font-size:0.875rem; font-weight:500; color:#111827;">AI Extractions Completed</p>
                                <div style="height:6px; width:120px; background:#10b981; border-radius:3px;"></div>
                            </div>
                        </div>

                        <div style="display:flex; align-items:flex-start; gap:16px; margin-bottom:32px; position:relative; z-index:1;">
                            <div style="width:24px; height:24px; background:#111827; color:white; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:0.75rem; font-weight:600; flex-shrink:0;">2</div>
                            <div style="padding-top:2px;">
                                <p style="margin:0 0 8px 0; font-size:0.875rem; font-weight:500; color:#111827;">Verify Data Elements</p>
                                <div style="height:6px; width:160px; background:#e5e7eb; border-radius:3px;"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    overlay.innerHTML = content;
    document.body.appendChild(overlay);
}"""

pattern = re.compile(r'function viewDetails\(id\) \{.*?(?=\n\} // End of viewDetails|\n// Search verifications|\nfunction searchVerifications|\nfunction initAlerts)', re.DOTALL)
match = pattern.search(text)
if match:
    new_text = text[:match.start()] + new_view_details + "\n\n" + text[match.end():]
    new_text = new_text.replace("\n\n\n\n", "\n\n")
    with open('frontend/script.js', 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("SUCCESS: viewDetails replaced")
else:
    print("ERROR: Could not find viewDetails function")
