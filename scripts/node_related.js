
let nodes = []; 
let edges = []; 
let allSockets = new Map(); 

const editorContainer = document.getElementById('editor-container');
const nodeGraph = document.getElementById('node-graph');
const edgeSVG = document.getElementById('edge-svg');
const saveBtn = document.getElementById('save-btn');
const loadBtn = document.getElementById('load-btn');


let state = {
    offsetX: 0,
    offsetY: 0,
    scale: 1.0,
    isDraggingNode: false,
    draggedNode: null,
    isPanning: false,
    panStart: { x: 0, y: 0 },
    isDrawingEdge: false,
    draggedSocket: null,
    currentEdgeLine: null,
    pendingStartSocket: null, 
    mouse: { x: 0, y: 0 }
};

const nodePresets = [
    { 
        name: 'Position', 
        inOut: [
            { name: 'X', type: 'float', isOutput: true }, 
            { name: 'Y', type: 'float', isOutput: true }, 
            { name: 'Z', type: 'float', isOutput: true }
        ]},
    { 
        name: 'Move', 
        inOut: [
            { name: 'X', type: 'float', isInput: true }, 
            { name: 'Y', type: 'float', isInput: true }, 
            { name: 'Z', type: 'float', isInput: true },
            { name: 'X', type: 'int', isInput: false },
            { name: 'Y', type: 'int', isInput: false }, 
            { name: 'Z', type: 'int', isInput: false }
        ]
    }
];

function drawBezierPath(startPos, endPos) {
    const p1 = startPos;
    const p4 = endPos;
    
    const dx = Math.max(50, Math.abs(p4.x - p1.x) / 3);
    const offsetDirection = p1.x < p4.x ? 1 : -1;
    
    const p2 = { x: p1.x + dx * offsetDirection, y: p1.y };
    const p3 = { x: p4.x - dx * offsetDirection, y: p4.y };

    return `M${p1.x},${p1.y} C${p2.x},${p2.y} ${p3.x},${p3.y} ${p4.x},${p4.y}`;
}

function updateGraphTransform() {
    nodeGraph.style.transform = `translate(${state.offsetX}px, ${state.offsetY}px) scale(${state.scale})`;
    drawConnection();
}

function getSocketAbsolutePosition(socketElement) {
    const rect = socketElement.getBoundingClientRect();
    return {
        x: rect.left + rect.width / 2,
        y: rect.top + rect.height / 2
    };
}

function typeCheck(type1, type2) {
    if (type1 === type2) return true;
    if ((type1 === "float" && type2 === "int") || (type1 === "int" && type2 === "float")) return true;
    return false;
}

function createNode(nodeData, x, y,  id) {
    
    // Initalizing the Node itself
    const nodeElement = document.createElement('div');
    nodeElement.className = 'node';
    nodeElement.dataset.id = id;
    nodeElement.style.left = `${x}px`;
    nodeElement.style.top = `${y}px`;
    nodeElement.nodeData = {x, y, id, nodeData};

    // Header
    const header = document.createElement('div');
    header.className = 'node-header';

    // Closing Node Button
    const closeBtn = document.createElement('span');
    closeBtn.className = 'header-btn close-btn';
    closeBtn.textContent = 'X';
    closeBtn.addEventListener('click', (e) => {
        deleteNode(nodeEl);
        e.stopPropagation();
    });

    // Closing Node Button
    const minimizeBtn = document.createElement('span');
    minimizeBtn.className = 'header-btn min-btn';
    minimizeBtn.textContent = 'V';

    // title
    const title = document.createElement('span');
    title.className = 'node-title';
    title.textContent = nodeData.name;
    header.appendChild(title);

    header.appendChild(closeBtn);
    
    nodeElement.appendChild(header);

    // Body & Sockets

    const body = document.createElement('div');
    nodeElement.appendChild(body);
    const inOut = nodeData.inOut;
    console.log(nodeData)

    const maxSockets = inOut.length;

    for (let i = 0; i < maxSockets; i++) {
        const data = inOut[i];
        console.log(data.isInput)
        const row = document.createElement('div');
        row.className = 'socket-row';
        const socket = createSocket(nodeElement, data, data.isInput);
        const nameSpan = document.createElement('span');
        nameSpan.textContent = data.name;
        // Input Socket
        
        if (data.isInput) {
            
            socket.className = 'socket input';
            socket.type = "float";
            socket.name = "Value In";
            row.appendChild(nameSpan);
            row.appendChild(socket);
        } else {
            socket.className = 'socket output';
            socket.type = "float";
            socket.name = "Value Out";
            row.appendChild(socket);
            row.appendChild(nameSpan);
            
        }
        body.appendChild(row);
    }

    // Bottom Sockets(currently ignored)

    nodeGraph.appendChild(nodeElement);
    nodes.push(nodeElement);

    return nodeElement;
}

function createSocket(nodeElement, socketData, inOut) {
    const nodeId = nodeElement.dataset.id;
    const socketElement = document.createElement('div');
    socketElement.className = `socket ${inOut ? 'in' : 'out'}`;
    socketElement.type = socketData.type;
    socketElement.inOut = inOut;
    socketElement.nodeId = nodeId;

    if (socketData.type === 'float') {
            socketElement.style.backgroundColor = '#ffff00';
    } else if (socketData.type === 'int') {
            socketElement.style.backgroundColor = '#0000ff';
    } else {
        socketElement.style.backgroundColor = '#242424';
    }
    const key = `${nodeId}-${socketData.name}-${inOut ? 'in' : 'out'}`;
    allSockets.set(key, socketElement);
    return socketElement
}

function createConnection() {
    const isDuplicate = edges.some(edge => (edge.startElement === startSocketElement && edge.endElement === endSocketElement));
    console.log(isDuplicate);
    if (isDuplicate) return;

    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.className = 'edge-path'; 
    path.setAttribute('fill', 'none');
    path.setAttribute('stroke', startSocketElement.style.backgroundColor || '#f0f0f0');
    path.setAttribute('stroke-width', '3');

    const newConnection = {
        startElement: startSocketElement,
        endElement: endSocketElement,
        pathElement: path
    };

    edges.push(newEdge);
    edgeSVG.appendChild(path);

    path.addEventListener('click', (e) => {
        deleteConnection(newEdge);
        e.stopPropagation(); 
    });

    drawConnection();
}

function drawConnection() {
    const editorRect = editorContainer.getBoundingClientRect();
    
    edges.forEach(edge => {
        if (!edge.startElement || !edge.endElement) return;
        
        const startPos = getSocketAbsolutePosition(edge.startElement);
        const endPos = getSocketAbsolutePosition(edge.endElement);
        
        startPos.x -= editorRect.left;
        startPos.y -= editorRect.top;
        endPos.x -= editorRect.left;
        endPos.y -= editorRect.top;
        
        const d = drawBezierPath(startPos, endPos);
        edge.pathElement.setAttribute('d', d);
    });
    
    if (state.currentEdgeLine && state.draggedSocket) {
        const startPos = getSocketAbsolutePosition(state.draggedSocket);
        
        startPos.x -= editorRect.left;
        startPos.y -= editorRect.top;
        
        const mousePos = { x: state.mouse.x - editorRect.left, y: state.mouse.y - editorRect.top };
        
        const d = drawBezierPath(startPos, mousePos);
        state.currentEdgeLine.setAttribute('d', d);
    }
}

function checkAndCreateConnection(startSocketElement, targetSocketElement) {
    // mostly taken from ai
    console.log('Test1');
    if (startSocketElement.dataset.nodeId === targetSocketElement.dataset.nodeId) return;

    const startIsInput = startSocket.dataset.isInput === 'true';
    const targetIsInput = targetSocket.dataset.isInput === 'true'; //! must be False?
    console.log('Test2');
    if (startIsInput === targetIsInput) return; 
    
    const [outSocket, inSocket] = startIsInput ? [targetSocket, startSocket] : [startSocket, targetSocket];
    console.log('Test3');
    if (!typeCheck(outSocket.dataset.type, inSocket.dataset.type)) {
        console.log(`❌ Verbindung ABGELEHNT: Typen inkompatibel (${outSocket.dataset.type} -> ${inSocket.dataset.type}).`);
        return;
    }
    console.log('Test4');
    createConnection(outSocket, inSocket);

}

editorContainer.addEventListener('mousedown', (e) => {
    state.mouse = { x: e.clientX, y: e.clientY };

    const target = e.target;
    const clickedSocket = target.closest('.socket');

    // 1. ZWEITER KLICK FÜR VERBINDUNG HERSTELLEN 
    if (clickedSocket && state.pendingStartSocket) {
        
        checkAndCreateConnection(state.pendingStartSocket, clickedSocket);
        
        state.pendingStartSocket = null;
        state.draggedSocket = null;
        if (state.currentEdgeLine) {
                state.currentEdgeLine.remove();
                state.currentEdgeLine = null;
        }
        state.isDrawingEdge = false;
        e.stopPropagation();
        return;
    }

    // 2. ERSTER KLICK / START DRAG FÜR KANTE 
    if (clickedSocket) {
        state.draggedSocket = clickedSocket;
        state.isDrawingEdge = true;
        
        state.currentEdgeLine = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        state.currentEdgeLine.setAttribute('fill', 'none');
        state.currentEdgeLine.setAttribute('stroke', clickedSocket.style.backgroundColor || 'white');
        state.currentEdgeLine.setAttribute('stroke-width', '3');
        state.currentEdgeLine.setAttribute('stroke-dasharray', '5,5');
        edgeSVG.appendChild(state.currentEdgeLine);
        
        drawConnection(); 
        e.stopPropagation();
        return;
    }
    
    // 3. NODE DRAGGING
    const draggedNodeHeader = target.closest('.node-header');
    if (draggedNodeHeader && !target.closest('.header-btn')) { 
        const nodeEl = draggedNodeHeader.closest('.node');
        state.isDraggingNode = true;
        state.draggedNode = nodeEl;
        
        const rect = nodeEl.getBoundingClientRect();
        const nodeGraphRect = nodeGraph.getBoundingClientRect();
        
        state.dragOffset = {
            x: e.clientX - rect.left - (nodeGraphRect.left - state.offsetX),
            y: e.clientY - rect.top - (nodeGraphRect.top - state.offsetY)
        };
        
        nodeEl.style.zIndex = 11; 
        editorContainer.style.cursor = 'grabbing';
        e.stopPropagation();
        return;
    }
    
    // 4. PANNING
    if (e.button === 0) { 
        state.isPanning = true;
        state.panStart.x = e.clientX - state.offsetX;
        state.panStart.y = e.clientY - state.offsetY;
        editorContainer.style.cursor = 'grabbing';
    }
});

document.addEventListener('mousemove', (e) => {
    state.mouse = { x: e.clientX, y: e.clientY };
    
    if (state.isDrawingEdge || state.pendingStartSocket) {
        
        if (state.pendingStartSocket && !state.currentEdgeLine) {
            state.draggedSocket = state.pendingStartSocket; 
            state.isDrawingEdge = true;
            
            state.currentEdgeLine = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            state.currentEdgeLine.setAttribute('fill', 'none');
            state.currentEdgeLine.setAttribute('stroke', state.draggedSocket.style.backgroundColor || 'white');
            state.currentEdgeLine.setAttribute('stroke-width', '3');
            state.currentEdgeLine.setAttribute('stroke-dasharray', '5,5'); 
            edgeSVG.appendChild(state.currentEdgeLine);
        }

        drawConnection();
        return;
    }

    if (state.isDraggingNode && state.draggedNode) {
        const nodeEl = state.draggedNode;
        
        nodeEl.nodeData.x = (e.clientX - state.offsetX - state.dragOffset.x) / state.scale;
        nodeEl.nodeData.y = (e.clientY - state.offsetY - state.dragOffset.y) / state.scale;

        nodeEl.style.left = `${nodeEl.nodeData.x}px`;
        nodeEl.style.top = `${nodeEl.nodeData.y}px`;
        drawConnection(); 
        return;
    }
    
    if (state.isPanning) {
        state.offsetX = e.clientX - state.panStart.x;
        state.offsetY = e.clientY - state.panStart.y;
        updateGraphTransform();
    }
});

document.addEventListener('mouseup', (e) => {
    if (state.isDraggingNode && state.draggedNode) {
        state.draggedNode.style.zIndex = 10;
    }
    state.isDraggingNode = false;
    state.draggedNode = null;
    state.isPanning = false;
    editorContainer.style.cursor = 'grab';

    if (state.isDrawingEdge && state.draggedSocket) {
        if (state.currentEdgeLine) {
            state.currentEdgeLine.remove();
            state.currentEdgeLine = null;
        }

        state.pendingStartSocket = state.draggedSocket;
        state.isDrawingEdge = false;
        state.draggedSocket = null;
    }
});

editorContainer.addEventListener('wheel', (e) => {
    e.preventDefault();
    const oldScale = state.scale;
    
    const zoomFactor = 1 + (e.deltaY < 0 ? 0.1 : -0.1);
    state.scale = Math.max(0.5, Math.min(3.0, state.scale * zoomFactor)); 

    const mouseX = e.clientX;
    const mouseY = e.clientY;

    const worldX = (mouseX - state.offsetX) / oldScale;
    const worldY = (mouseY - state.offsetY) / oldScale;

    state.offsetX = mouseX - worldX * state.scale;
    state.offsetY = mouseY - worldY * state.scale;
    
    updateGraphTransform();
});

function init() {
    createNode(nodePresets[1], 300, 50);
    createNode(nodePresets[0], 50, 50);
}
init();