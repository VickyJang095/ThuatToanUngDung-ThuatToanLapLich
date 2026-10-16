const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
// DOM tối thiểu để kiểm tra các nhánh kết quả mà không cần trình duyệt.
class Element {
    constructor() { this.children = []; this.style = {}; this.cells = []; this.textContent = ''; }
    set innerHTML(value) { this.html = value; this.children = []; this.cells = Array.from(value.matchAll(/<td>/g), () => new Element()); }
    get innerHTML() { return this.html; }
    appendChild(child) { this.children.push(child); }
    addEventListener() {}
}
const elements = new Map();
const document = {
    getElementById(id) { if (!elements.has(id)) elements.set(id, new Element()); return elements.get(id); },
    createElement() { return new Element(); },
};
const context = vm.createContext({ document, window: { addEventListener() {} } });
vm.runInContext(fs.readFileSync('static/app.js', 'utf8'), context);
for (const status of ['OPTIMAL', 'FEASIBLE', 'UNKNOWN', 'UNAVAILABLE']) {
    const solved = ['OPTIMAL', 'FEASIBLE'].includes(status);
    const cp = { status, optimal: status === 'OPTIMAL', objective: solved ? 0 : null,
        schedule: solved ? [{ machine: 1, jobs: [{ id: 1, start: 0, end: 2, d: 3 }] }] : null,
        makespan: solved ? 2 : null, runtime: 0, best_bound: solved ? 0 : null, message: 'Thiếu OR-Tools: pip install -r requirements.txt' };
    context.data = { greedy: cp, ga: cp, bb: cp, ts: cp, cp_sat: cp };
    vm.runInContext('updateSummary(data); renderTable(data); renderGantt(data);', context);
    assert.equal(elements.get('cp_satObjective').textContent, solved ? 0 : '-');
    const label = elements.get('cpStatus').textContent;
    assert.ok(label.includes(status === 'OPTIMAL' ? 'Cận chi phí trễ' : status === 'FEASIBLE' ? 'Có lịch khả thi' : status === 'UNAVAILABLE' ? 'pip install' : 'Chưa có lời giải'));
    assert.ok(!label.includes('Đã chứng minh tối ưu'));
    vm.runInContext('renderConclusions(data)', context);
    const conclusions = elements.get('comparisonConclusions').children.map(p => p.textContent).join(' ');
    assert.ok(conclusions.includes(solved ? 'Chi phí trễ thấp nhất' : 'Chưa có lịch khả thi'));
    assert.equal(elements.get('resultTableBody').children.length, 5);
    assert.equal(elements.get('ganttContainer').children.length, 5);
}
console.log('PASS: frontend OPTIMAL, FEASIBLE, UNKNOWN, UNAVAILABLE; null objective; bảng và Gantt.');

(async () => {
    let attempted = 0;
    context.action = async () => {
        attempted++;
        assert.equal(elements.get('runBtn').disabled, true);
    };
    await vm.runInContext("runAction(action, 'Đang chạy')", context);
    assert.equal(attempted, 1);
    assert.equal(elements.get('runBtn').disabled, false);
    assert.equal(elements.get('runStatus').textContent, 'Hoàn tất.');
    context.action = async () => { throw new Error('Test server error'); };
    await vm.runInContext("runAction(action, 'Đang chạy')", context);
    assert.equal(elements.get('runBtn').disabled, false);
    assert.equal(elements.get('generateBtn').disabled, false);
    assert.ok(elements.get('runStatus').textContent.includes('Test server error'));
    console.log('PASS: trạng thái đang chạy, hoàn tất và lỗi; khôi phục nút.');
})().catch(error => { console.error(error); process.exitCode = 1; });
