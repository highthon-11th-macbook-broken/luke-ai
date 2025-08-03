// 대시보드 JavaScript 기능

document.addEventListener('DOMContentLoaded', function() {
    // 초기 데이터 로드
    loadRecentRequests();
    loadRequestsTable();
    
    // 폼 제출 이벤트
    document.getElementById('detectionForm').addEventListener('submit', function(e) {
        e.preventDefault();
        submitDetectionRequest();
    });
    
    // 실시간 상태 업데이트 (처리중인 요청이 있으면 더 자주 업데이트)
    setInterval(function() {
        updateProcessingRequests();
    }, 3000); // 3초마다 처리중인 요청 확인 (더 자주)
    
    // 일반 데이터 새로고침 (15초마다)
    setInterval(function() {
        loadRecentRequests();
        loadRequestsTable();
    }, 15000);
});

// 탐지 요청 제출
async function submitDetectionRequest() {
    const form = document.getElementById('detectionForm');
    const formData = new FormData(form);
    
    const data = {
        email: formData.get('email') || null,
        phone: formData.get('phone') || null,
        name: formData.get('name') || null
    };
    
    // 최소 하나의 필드가 필요
    if (!data.email && !data.phone && !data.name) {
        showAlert('최소 하나의 탐지 대상이 필요합니다.', 'warning');
        return;
    }
    
    try {
        // 제출 버튼 비활성화
        const submitButton = form.querySelector('button[type="submit"]');
        const originalText = submitButton.innerHTML;
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 탐지 시작 중...';
        
        const response = await fetch('/detection/detect', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            const result = await response.json();
            showAlert('탐지 요청이 성공적으로 생성되었습니다! 처리 중입니다...', 'success');
            form.reset();
            
            // 즉시 UI 업데이트
            setTimeout(() => {
                loadRecentRequests();
                loadRequestsTable();
            }, 500);
            
            // 1초 후 다시 업데이트
            setTimeout(() => {
                loadRecentRequests();
                loadRequestsTable();
            }, 1000);
            
            // 3초 후 다시 업데이트
            setTimeout(() => {
                loadRecentRequests();
                loadRequestsTable();
            }, 3000);
            
        } else {
            const error = await response.json();
            showAlert('탐지 요청 생성 실패: ' + error.detail, 'danger');
        }
    } catch (error) {
        showAlert('서버 연결 오류가 발생했습니다.', 'danger');
    } finally {
        // 제출 버튼 다시 활성화
        const submitButton = form.querySelector('button[type="submit"]');
        submitButton.disabled = false;
        submitButton.innerHTML = originalText;
    }
}

// 최근 요청 로드
async function loadRecentRequests() {
    try {
        const response = await fetch('/detection/requests?limit=5');
        const requests = await response.json();
        
        const container = document.getElementById('recentRequests');
        
        if (requests.length === 0) {
            container.innerHTML = '<p class="text-muted">아직 탐지 요청이 없습니다.</p>';
            return;
        }
        
        let html = '';
        requests.forEach(request => {
            const statusClass = getStatusBadgeClass(request.status);
            const statusText = getStatusText(request.status);
            const targetValue = request.target_email || request.target_phone || request.target_name || 'N/A';
            
            // 처리중인 요청은 특별한 스타일 적용
            const isProcessing = request.status === 'processing';
            const itemClass = isProcessing ? 'processing-item' : '';
            
            html += `
                <div class="d-flex justify-content-between align-items-center mb-2 ${itemClass}">
                    <div>
                        <strong>${targetValue}</strong>
                        <br>
                        <small class="text-muted">${formatDate(request.created_at)}</small>
                    </div>
                    <span class="badge status-badge ${statusClass}">${statusText}</span>
                </div>
            `;
        });
        
        container.innerHTML = html;
        
        // 처리중인 요청이 있으면 시각적 피드백 추가
        const processingRequests = requests.filter(req => req.status === 'processing');
        if (processingRequests.length > 0) {
            console.log(`🔄 ${processingRequests.length}개의 요청이 처리중입니다...`);
        }
        
    } catch (error) {
        console.error('최근 요청 로드 실패:', error);
    }
}

// 요청 테이블 로드
async function loadRequestsTable() {
    try {
        const response = await fetch('/detection/requests');
        const requests = await response.json();
        
        const tbody = document.getElementById('requestsTable');
        
        if (requests.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted">아직 탐지 요청이 없습니다.</td></tr>';
            return;
        }
        
        let html = '';
        requests.forEach(request => {
            html += `
                <tr>
                    <td>${request.id}</td>
                    <td>${request.target_email || '-'}</td>
                    <td>${request.target_phone || '-'}</td>
                    <td>${request.target_name || '-'}</td>
                    <td><span class="badge status-badge status-${request.status}">${getStatusText(request.status)}</span></td>
                    <td>${formatDate(request.created_at)}</td>
                    <td>${request.completed_at ? formatDate(request.completed_at) : '-'}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary" onclick="viewResults(${request.id})">
                            <i class="fas fa-eye"></i> 결과보기
                        </button>
                    </td>
                </tr>
            `;
        });
        
        tbody.innerHTML = html;
    } catch (error) {
        console.error('요청 테이블 로드 실패:', error);
    }
}

// 처리중인 요청 실시간 업데이트
async function updateProcessingRequests() {
    try {
        const response = await fetch('/detection/requests');
        const requests = await response.json();
        
        // 처리중인 요청이 있는지 확인
        const processingRequests = requests.filter(req => req.status === 'processing');
        const pendingRequests = requests.filter(req => req.status === 'pending');
        
        if (processingRequests.length > 0 || pendingRequests.length > 0) {
            // 처리중이거나 대기중인 요청이 있으면 즉시 UI 업데이트
            loadRecentRequests();
            loadRequestsTable();
            console.log(`🔄 ${processingRequests.length}개 처리중, ${pendingRequests.length}개 대기중...`);
            
            // 처리중인 요청이 있으면 더 자주 업데이트
            if (processingRequests.length > 0) {
                setTimeout(() => {
                    loadRecentRequests();
                    loadRequestsTable();
                }, 2000); // 2초 후 다시 업데이트
            }
        }
    } catch (error) {
        console.error('실시간 업데이트 실패:', error);
    }
}

// 결과 보기
async function viewResults(requestId) {
    try {
        const response = await fetch(`/detection/requests/${requestId}`);
        const request = await response.json();
        
        const modalBody = document.getElementById('resultModalBody');
        
        let html = `
            <div class="mb-3">
                <h6>탐지 대상</h6>
                <p>
                    <strong>이메일:</strong> ${request.target_email || '-'}<br>
                    <strong>전화번호:</strong> ${request.target_phone || '-'}<br>
                    <strong>이름:</strong> ${request.target_name || '-'}
                </p>
            </div>
        `;
        
        if (request.results && request.results.length > 0) {
            html += '<h6>탐지 결과</h6>';
            request.results.forEach(result => {
                const riskClass = getRiskClass(result.risk_score);
                const resultClass = result.is_leaked ? 'result-leaked' : 
                                  result.risk_score >= 0.8 ? 'result-high-risk' : 'result-safe';
                
                html += `
                    <div class="result-item ${resultClass}">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <strong>${result.target_value}</strong>
                                <br>
                                <small class="text-muted">${result.detection_type}</small>
                            </div>
                            <span class="risk-score ${riskClass}">${(result.risk_score * 100).toFixed(1)}%</span>
                        </div>
                        <p class="mt-2 mb-1"><strong>증거:</strong> ${result.evidence || 'N/A'}</p>
                        ${result.source_url ? `<p class="mb-0"><strong>출처:</strong> <a href="${result.source_url}" target="_blank">${result.source_url}</a></p>` : ''}
                    </div>
                `;
            });
        } else {
            html += '<div class="alert alert-info">아직 탐지 결과가 없습니다.</div>';
        }
        
        modalBody.innerHTML = html;
        
        // 모달 표시
        const modal = new bootstrap.Modal(document.getElementById('resultModal'));
        modal.show();
    } catch (error) {
        showAlert('결과 로드 실패: ' + error.message, 'danger');
    }
}

// 상태 텍스트 변환
function getStatusText(status) {
    const statusMap = {
        'pending': '대기중',
        'processing': '처리중',
        'completed': '완료',
        'failed': '실패'
    };
    return statusMap[status] || status;
}

// 상태 배지 클래스 반환
function getStatusBadgeClass(status) {
    const classMap = {
        'pending': 'status-pending',
        'processing': 'status-processing',
        'completed': 'status-completed',
        'failed': 'status-failed'
    };
    return classMap[status] || 'status-unknown';
}

// 위험도 클래스 반환
function getRiskClass(riskScore) {
    if (riskScore >= 0.8) return 'risk-high';
    if (riskScore >= 0.5) return 'risk-medium';
    return 'risk-low';
}

// 날짜 포맷팅
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('ko-KR');
}

// 알림 표시
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // 5초 후 자동 제거
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
} 