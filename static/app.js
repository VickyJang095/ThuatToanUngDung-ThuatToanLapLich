const algorithmItems = [
    { key: 'greedy', label: 'Greedy' }, { key: 'ga', label: 'GA' },
    { key: 'bb', label: 'B&B' }, { key: 'ts', label: 'TS' },
    { key: 'cp_sat', label: 'CP-SAT' },
];

function cpStatus(entry) {
    if (!entry) return 'Chưa có lời giải';
    if (entry.optimal && entry.status === 'OPTIMAL') return 'Đã chứng minh tối ưu';
    if (entry.schedule !== null && entry.objective != null) return 'Có lịch khả thi';
    if (entry.status === 'UNAVAILABLE') return entry.message;
    return 'Chưa có lời giải';
}

const state = {
    jobs: [],
    algorithms: {},
    busy: false,
};

function renderJobs(jobs) {
    const tbody = document.getElementById('jobsTableBody');
    tbody.innerHTML = '';
    document.getElementById('jobsCountLabel').textContent = `${jobs.length} công việc`;
    if (!jobs.length) {
        const row = document.createElement('tr');
        const cell = document.createElement('td');
        cell.colSpan = 4;
        cell.textContent = 'Chưa có dữ liệu';
        row.appendChild(cell);
        tbody.appendChild(row);
        return;
    }
    jobs.forEach(job => {
        const row = document.createElement('tr');
        for (const field of ['id', 'p', 'd', 'w']) {
            const cell = document.createElement('td');
            cell.textContent = job[field];
            row.appendChild(cell);
        }
        tbody.appendChild(row);
    });
}

function renderTable(data) {
    const tbody = document.getElementById('resultTableBody');
    tbody.innerHTML = '';

    const algorithms = algorithmItems;

    algorithms.forEach(item => {
        const entry = data[item.key];
        if (!entry || entry.objective === null || entry.objective === undefined) {
            const row = document.createElement('tr');
            row.innerHTML = `<td>${item.label}</td><td>-</td><td>${entry?.runtime != null ? entry.runtime + 's' : '-'}</td><td>-</td>`;
            if (item.key === 'cp_sat' && entry?.objective == null) {
                const status = document.createElement('small');
                status.textContent = ` — ${cpStatus(entry)} (${entry?.status ?? '-'})`;
                row.cells[0].appendChild(status);
            }
            tbody.appendChild(row);
            return;
        }

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.label}</td>
            <td>${entry.objective}</td>
            <td>${entry.runtime !== null ? entry.runtime + 's' : '-'}</td>
            <td>${entry.makespan !== null ? entry.makespan : '-'}</td>
        `;
        if (item.key === 'cp_sat' && entry?.objective == null) {
            const status = document.createElement('small');
            status.textContent = ` — ${cpStatus(entry)} (${entry.status})`;
            row.cells[0].appendChild(status);
        }
        tbody.appendChild(row);
    });
}

function renderConclusions(data) {
    const container = document.getElementById('comparisonConclusions');
    container.innerHTML = '';
    // Chỉ so sánh thuật toán có lịch và chi phí hợp lệ; null không phải 0.
    const valid = algorithmItems.filter(({ key }) =>
        Number.isFinite(data[key]?.objective) && Array.isArray(data[key]?.schedule));
    const add = text => {
        const paragraph = document.createElement('p');
        paragraph.textContent = text;
        container.appendChild(paragraph);
    };
    if (!valid.length) {
        add('Chưa có lịch khả thi để so sánh.');
        return;
    }
    const winners = field => {
        const entries = valid.filter(({ key }) => Number.isFinite(data[key][field]));
        const value = Math.min(...entries.map(({ key }) => data[key][field]));
        return { value, names: entries.filter(({ key }) => data[key][field] === value)
            .map(item => item.label).join(', ') };
    };
    const objective = winners('objective');
    add(`Chi phí trễ thấp nhất: ${objective.names} (objective = ${objective.value}).`);
    const runtime = winners('runtime');
    if (runtime.names) add(`Chạy nhanh nhất: ${runtime.names} (${runtime.value} giây). Runtime hiển thị đã làm tròn; các giá trị bằng nhau được xem là đồng hạng.`);
    const makespan = winners('makespan');
    if (makespan.names) add(`Hoàn thành toàn bộ công việc sớm nhất: ${makespan.names} (makespan = ${makespan.value} giờ).`);
    const candidates = valid.filter(({ key }) => data[key].objective === objective.value);
    const bestSpan = Math.min(...candidates.map(({ key }) =>
        Number.isFinite(data[key].makespan) ? data[key].makespan : Infinity));
    const shorter = candidates.filter(({ key }) =>
        (Number.isFinite(data[key].makespan) ? data[key].makespan : Infinity) === bestSpan);
    const bestRuntime = Math.min(...shorter.map(({ key }) =>
        Number.isFinite(data[key].runtime) ? data[key].runtime : Infinity));
    const preferred = shorter.filter(({ key }) =>
        (Number.isFinite(data[key].runtime) ? data[key].runtime : Infinity) === bestRuntime);
    add(`Đề xuất trên bộ dữ liệu này: ${preferred.map(item => item.label).join(', ')}. Thứ tự xét: objective thấp nhất → makespan nhỏ nhất → runtime ngắn nhất. Đây là cách chọn để so sánh, không thay đổi mục tiêu của các thuật toán.`);
    if (data.bb?.status === 'TIME_LIMIT') add('B&B đã hết giới hạn 5 giây: kết quả là lịch tốt nhất tìm được, chưa chứng minh chi phí tối ưu.');
    const excluded = algorithmItems.filter(item => !valid.includes(item));
    if (excluded.length) add(`Không đưa vào so sánh vì chưa có lịch: ${excluded.map(item => item.label).join(', ')}.`);
}

function updateSummary(data) {
    for (const key of ['ts', 'cp_sat']) {
        document.getElementById(`${key}Objective`).textContent = data[key]?.objective ?? '-';
        document.getElementById(`${key}Runtime`).textContent = data[key]?.runtime != null ? `${data[key].runtime}s` : '-';
    }
    const cp = data.cp_sat;
    document.getElementById('cpStatus').textContent = cp?.optimal
        ? `Cận chi phí trễ: ${cp.best_bound ?? '-'}`
        : `${cpStatus(cp)} — Cận: ${cp?.best_bound ?? '-'}`;

    document.getElementById('lptObjective').textContent = data.greedy.objective ?? '-';
    document.getElementById('gaObjective').textContent = data.ga.objective ?? '-';
    document.getElementById('bbObjective').textContent = data.bb.objective ?? '-';

    document.getElementById('lptRuntime').textContent = data.greedy.runtime ? `${data.greedy.runtime}s` : '-';
    document.getElementById('gaRuntime').textContent = data.ga.runtime ? `${data.ga.runtime}s` : '-';
    document.getElementById('bbRuntime').textContent = data.bb.runtime ? `${data.bb.runtime}s` : '-';
}

function renderGantt(algorithms) {
    const container = document.getElementById('ganttContainer');
    container.innerHTML = '';

    const machineBackgrounds = [
        'rgba(94, 201, 255, 0.2)',
        'rgba(120, 224, 169, 0.2)',
        'rgba(244, 191, 105, 0.2)',
        'rgba(255, 139, 123, 0.2)',
        'rgba(199, 168, 255, 0.2)',
        'rgba(122, 215, 209, 0.2)'
    ];

    const renderOne = (title, schedule, totalRange) => {
        const card = document.createElement('div');
        card.className = 'gantt-card';

        const heading = document.createElement('h3');
        heading.textContent = title;
        card.appendChild(heading);

        const legend = document.createElement('div');
        legend.className = 'gantt-legend';
        schedule.forEach((_, index) => {
            const item = document.createElement('span');
            item.className = 'gantt-legend-item';
            item.innerHTML = `<i style="background:${machineBackgrounds[index % machineBackgrounds.length]}; border: 1px solid rgba(255,255,255,0.2);"></i> M${index + 1}`;
            legend.appendChild(item);
        });
        card.appendChild(legend);

        // Cùng một thang giờ cho mọi thuật toán, bắt đầu từ thời điểm 0.
        const displayRange = Math.max(24, Math.ceil(totalRange / 6) * 6);
        const axis = document.createElement('div');
        axis.className = 'gantt-time-axis';
        for (let hour = 0; hour <= displayRange; hour += 6) {
            const tick = document.createElement('span');
            tick.textContent = `${hour}`;
            tick.style.left = `${hour / displayRange * 100}%`;
            axis.appendChild(tick);
        }
        card.appendChild(axis);

        const rows = [];

        schedule.forEach((machine, machineIndex) => {
            machine.jobs.forEach(job => {
                const row = document.createElement('div');
                row.className = 'gantt-task-row';

                const label = document.createElement('div');
                label.className = 'gantt-task-label';
                label.textContent = `Task ${job.id}`;

                const track = document.createElement('div');
                track.className = 'gantt-track';
                track.style.background = machineBackgrounds[machineIndex % machineBackgrounds.length];

                const bar = document.createElement('div');
                const left = (job.start / Math.max(displayRange, 1)) * 100;
                const width = ((job.end - job.start) / Math.max(displayRange, 1)) * 100;
                bar.className = `gantt-bar ${job.end <= job.d ? 'green' : 'red'}`;
                bar.style.left = `${left}%`;
                bar.style.width = `${width}%`;
                bar.textContent = `J${job.id}`;
                bar.title = `Job ${job.id} | Machine ${machineIndex + 1} | Bắt đầu ${job.start} giờ | Kết thúc ${job.end} giờ | Hạn ${job.d} giờ`;
                track.appendChild(bar);

                row.appendChild(label);
                row.appendChild(track);
                rows.push(row);
            });
        });

        rows.forEach(row => card.appendChild(row));
        container.appendChild(card);
    };

    const maxTime = Math.max(1, ...algorithmItems.map(item => algorithms[item.key]?.makespan ?? 0));
    algorithmItems.forEach(item => {
        const entry = algorithms[item.key];
        const title = item.key === 'cp_sat' && !entry?.optimal ? `${item.label} — ${cpStatus(entry)}` : item.label;
        renderOne(title, entry?.schedule ?? [], maxTime);
    });
}

async function runAction(action, message) {
    if (state.busy) return;
    state.busy = true;
    const runButton = document.getElementById('runBtn');
    const generateButton = document.getElementById('generateBtn');
    const status = document.getElementById('runStatus');
    runButton.disabled = true;
    generateButton.disabled = true;
    runButton.textContent = 'Đang xử lý…';
    status.textContent = message;
    try {
        await action();
        status.textContent = 'Hoàn tất.';
    } catch (error) {
        status.textContent = `Không thực hiện được: ${error.message}`;
    } finally {
        state.busy = false;
        runButton.disabled = false;
        generateButton.disabled = false;
        runButton.textContent = 'Chạy thuật toán';
    }
}

async function readResponse(res) {
    const type = res.headers.get('content-type') ?? '';
    if (!type.includes('application/json')) {
        throw new Error(`Máy chủ trả lỗi HTTP ${res.status}. Kiểm tra cửa sổ chạy Flask.`);
    }
    const data = await res.json();
    if (!res.ok) throw new Error(data.error ?? `Lỗi HTTP ${res.status}`);
    return data;
}

async function callGenerate() {
    const machineCount = Number(document.getElementById('machineCount').value);
    const jobCount = Number(document.getElementById('jobCount').value);
    const deadlineLevel = document.getElementById('deadlineLevel').value;

    const res = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ machines: machineCount, jobs: jobCount, deadline_level: deadlineLevel })
    });

    const data = await readResponse(res);
    document.getElementById('machineCount').value = data.machines;
    document.getElementById('jobCount').value = data.jobs.length;
    state.jobs = data.jobs;
    renderJobs(state.jobs);
}

async function callRun() {
    if (!state.jobs.length) await callGenerate();
    const machineCount = Number(document.getElementById('machineCount').value);
    const population = Number(document.getElementById('population').value);
    const generations = Number(document.getElementById('generations').value);
    const crossover = Number(document.getElementById('crossover').value);
    const mutation = Number(document.getElementById('mutation').value);

    const requestBody = {
        machines: machineCount,
        jobs: state.jobs,
        population,
        generations,
        crossover,
        mutation,
    };

    // Lưu và hiển thị đúng dữ liệu gửi đi, kể cả khi chưa bấm sinh dữ liệu.
    state.jobs = requestBody.jobs;
    renderJobs(state.jobs);

    const res = await fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
    });

    const data = await readResponse(res);
    state.algorithms = data;
    updateSummary(data);
    renderTable(data);
    renderConclusions(data);
    renderGantt(data);
}

document.getElementById('generateBtn').addEventListener('click', () => runAction(callGenerate, 'Đang sinh dữ liệu…'));
document.getElementById('runBtn').addEventListener('click', () => runAction(callRun, 'Đang chạy các thuật toán… B&B tối đa 5 giây, CP-SAT tối đa 10 giây.'));

window.addEventListener('DOMContentLoaded', () => {
    runAction(callGenerate, 'Đang sinh dữ liệu…');
});
