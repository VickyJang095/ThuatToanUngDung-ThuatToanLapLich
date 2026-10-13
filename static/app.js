const state = {
    jobs: [],
    algorithms: {},
};

function renderTable(data) {
    const tbody = document.getElementById('resultTableBody');
    tbody.innerHTML = '';

    const algorithms = [
        { key: 'greedy', label: 'Greedy' },
        { key: 'ga', label: 'GA' },
        { key: 'bb', label: 'B&B' },
    ];

    algorithms.forEach(item => {
        const entry = data[item.key];
        if (!entry || entry.objective === null || entry.objective === undefined) {
            const row = document.createElement('tr');
            row.innerHTML = `<td>${item.label}</td><td>-</td><td>-</td><td>-</td>`;
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
        tbody.appendChild(row);
    });
}

function updateSummary(data) {
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

    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const renderOne = (title, schedule, totalRange) => {
        const card = document.createElement('div');
        card.className = 'gantt-card';

        const heading = document.createElement('h3');
        heading.textContent = title;
        card.appendChild(heading);

        const monthRow = document.createElement('div');
        monthRow.className = 'gantt-months';
        months.forEach(month => {
            const span = document.createElement('span');
            span.textContent = month;
            monthRow.appendChild(span);
        });
        card.appendChild(monthRow);

        const rows = schedule.map((machine, index) => {
            const row = document.createElement('div');
            row.className = 'gantt-task-row';

            const label = document.createElement('div');
            label.className = 'gantt-task-label';
            label.textContent = `Machine ${index + 1}`;

            const track = document.createElement('div');
            track.className = 'gantt-track';

            machine.jobs.forEach(job => {
                const bar = document.createElement('div');
                const left = (job.start / Math.max(totalRange, 1)) * 100;
                const width = ((job.end - job.start) / Math.max(totalRange, 1)) * 100;
                bar.className = `gantt-bar ${job.end <= job.d ? 'green' : 'red'}`;
                bar.style.left = `${left}%`;
                bar.style.width = `${Math.max(width, 6)}%`;
                bar.textContent = `J${job.id}`;
                bar.title = `Job ${job.id} | Start ${job.start} | End ${job.end} | Deadline ${job.d}`;
                track.appendChild(bar);
            });

            row.appendChild(label);
            row.appendChild(track);
            return row;
        });

        rows.forEach(row => card.appendChild(row));
        container.appendChild(card);
    };

    const maxTime = Math.max(
        algorithms.greedy.makespan || 0,
        algorithms.ga.makespan || 0,
        algorithms.bb.makespan || 0,
        1
    );

    renderOne('Greedy', algorithms.greedy.schedule || [], maxTime);
    renderOne('B&B', algorithms.bb.schedule || [], maxTime);
    renderOne('GA', algorithms.ga.schedule || [], maxTime);
}

async function callGenerate() {
    const machineCount = Number(document.getElementById('machineCount').value);
    const jobCount = Number(document.getElementById('jobCount').value);

    const res = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ machines: machineCount, jobs: jobCount })
    });

    const data = await res.json();
    document.getElementById('machineCount').value = data.machines;
    document.getElementById('jobCount').value = data.jobs.length;
    state.jobs = data.jobs;
    console.log('Generated jobs:', data.jobs);
}

async function callRun() {
    const machineCount = Number(document.getElementById('machineCount').value);
    const jobCount = Number(document.getElementById('jobCount').value);
    const population = Number(document.getElementById('population').value);
    const generations = Number(document.getElementById('generations').value);
    const crossover = Number(document.getElementById('crossover').value);
    const mutation = Number(document.getElementById('mutation').value);

    const requestBody = {
        machines: machineCount,
        jobs: state.jobs.length ? state.jobs : Array.from({ length: jobCount }, (_, i) => ({
            id: i + 1,
            p: Math.floor(Math.random() * 15) + 3,
            d: Math.floor(Math.random() * 35) + 10,
            w: Math.floor(Math.random() * 5) + 1,
        })),
        population,
        generations,
        crossover,
        mutation,
    };

    const res = await fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
    });

    const data = await res.json();
    state.algorithms = data;
    updateSummary(data);
    renderTable(data);
    renderGantt(data);
}

document.getElementById('generateBtn').addEventListener('click', callGenerate);
document.getElementById('runBtn').addEventListener('click', callRun);

window.addEventListener('DOMContentLoaded', () => {
    callGenerate();
});
