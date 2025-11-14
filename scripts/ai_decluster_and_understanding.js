// JavaScript: Logik und Interaktion

const editorContainer = document.getElementById('editor-container');
const nodeGraph = document.getElementById('node-graph');
const edgeSVG = document.getElementById('edge-svg');
const saveBtn = document.getElementById('save-btn');
const loadBtn = document.getElementById('load-btn');

// Globale Zustände
let nodes = []; 
let edges = []; 
let allSockets = new Map(); 

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

// Node Presets, angepasst für 3D und die Farben im Bild
const nodePresets = [
    // Koordinaten Output (gelb, float)
    { name: 'Position', inputs: [], outputs: [{ name: 'X', type: 'float' }, { name: 'Y', type: 'float' }, { name: 'Z', type: 'float' }], color: '#ffff00' },
    // Move Node (mit 3D-Koordinaten Inputs und rotem ID/Exec Output)
    { 
        name: 'Move', 
        inputs: [
            { name: 'X', type: 'float' }, 
            { name: 'Y', type: 'float' }, 
            { name: 'Z', type: 'float' },
            { name: 'ID', type: 'exec', isBottom: true } // Spezieller Exec-Socket
        ], 
        outputs: [
            { name: 'X', type: 'int', pos: 'right' }, // Im Bild blau (int)
            { name: 'Y', type: 'int', pos: 'right' }, 
            { name: 'Z', type: 'int', pos: 'right' }
        ], 
        color: '#0000ff' 
    },
    // Execute Start (roter Socket)
    { name: 'Start', inputs: [], outputs: [{ name: 'Exec', type: 'exec', isBottom: true }], color: '#cc0000' }
];

// --- UTILITIES ---

function updateGraphTransform() {
    nodeGraph.style.transform = `translate(${state.offsetX}px, ${state.offsetY}px) scale(${state.scale})`;
    drawEdges();
}

function getSocketAbsolutePosition(socketElement) {
    const rect = socketElement.getBoundingClientRect();
    return {
        x: rect.left + rect.width / 2,
        y: rect.top + rect.height / 2
    };
}

// --- NODE RENDERING ---

function createNodeElement(nodeData, x, y, id = Date.now() + Math.random()) {
    const nodeEl = document.createElement('div');
    nodeEl.className = 'node';
    nodeEl.dataset.id = id; 
    nodeEl.style.left = `${x}px`;
    nodeEl.style.top = `${y}px`;
    nodeEl.nodeData = { x, y, id, ...nodeData }; 
    
    // Header
    const header = document.createElement('div');
    header.className = 'node-header';
    
    // Minimieren/Ausblenden Button (V)
    const minimizeBtn = document.createElement('span');
    minimizeBtn.className = 'header-btn minimize';
    minimizeBtn.textContent = 'V';
    header.appendChild(minimizeBtn);

    // Titel
    const title = document.createElement('span');
    title.className = 'node-title';
    title.textContent = nodeData.name;
    header.appendChild(title);
    
    // Schließen/Löschen Button (X)
    const closeBtn = document.createElement('span');
    closeBtn.className = 'header-btn close';
    closeBtn.textContent = 'X';
    closeBtn.addEventListener('click', (e) => {
        deleteNode(nodeEl);
        e.stopPropagation();
    });
    header.appendChild(closeBtn);
    
    nodeEl.appendChild(header);

    // Body und Sockets erstellen
    const body = document.createElement('div');
    body.style.paddingTop = '5px';
    nodeEl.appendChild(body);
    
    // Getrennte Listen für normale Sockets und Bottom-Sockets
    const normalInputs = nodeData.inputs.filter(s => !s.isBottom);
    const normalOutputs = nodeData.outputs.filter(s => !s.isBottom);
    const bottomSockets = [...nodeData.inputs.filter(s => s.isBottom), ...nodeData.outputs.filter(s => s.isBottom)];
    
    const maxNormalSockets = Math.max(normalInputs.length, normalOutputs.length);
    
    for (let i = 0; i < maxNormalSockets; i++) {
        const inputData = normalInputs[i];
        const outputData = normalOutputs[i];
        
        const row = document.createElement('div');
        row.className = 'socket-row';
        
        // Input Socket links (z.B. X, Y, Z)
        if (inputData) {
            const inputEl = createSocket(nodeEl, inputData, true);
            const nameSpan = document.createElement('span');
            nameSpan.textContent = inputData.name;
            
            row.appendChild(inputEl);
            row.appendChild(nameSpan);
            body.appendChild(row);
        }

        // Output Socket rechts (z.B. X, Y, Z)
        if (outputData) {
            // Erstellt die Output-Row nur, wenn ein Output vorhanden ist
            let outputRow = row;
            if (!inputData) { 
                outputRow = document.createElement('div');
                outputRow.className = 'socket-row';
                body.appendChild(outputRow);
            }
            
            const outputEl = createSocket(nodeEl, outputData, false);
            const nameSpan = document.createElement('span');
            nameSpan.textContent = outputData.name;
            
            outputRow.appendChild(nameSpan);
            outputRow.appendChild(outputEl);
        }
    }
    
    // Bottom Sockets (separater Platz)
    bottomSockets.forEach(socketData => {
            const isInput = !!nodeData.inputs.find(s => s.name === socketData.name && s.isBottom);
            const socketEl = createSocket(nodeEl, socketData, isInput);
            
            const bottomRow = document.createElement('div');
            bottomRow.className = 'bottom-socket-row';
            bottomRow.appendChild(socketEl);
            nodeEl.appendChild(bottomRow);
    });

    nodeGraph.appendChild(nodeEl);
    nodes.push(nodeEl);
    
    return nodeEl;
}

/** Hilfsfunktion zum Erstellen eines einzelnen Socket-Elements */
function createSocket(nodeEl, socketData, isInput) {
    const nodeId = nodeEl.dataset.id;
    const socketEl = document.createElement('div');
    socketEl.className = `socket ${isInput ? 'input' : 'output'}`;
    socketEl.dataset.type = socketData.type;
    socketEl.dataset.name = socketData.name;
    socketEl.dataset.isInput = isInput;
    socketEl.dataset.nodeId = nodeId;
    
    // Farbe wird über CSS-Klassen gesetzt, aber für die Kante wird sie manuell gesetzt
    if (socketData.type === 'exec') {
        socketEl.style.backgroundColor = '#cc0000';
    } else if (socketData.type === 'float') {
            socketEl.style.backgroundColor = '#ffff00';
    } else if (socketData.type === 'int') {
            socketEl.style.backgroundColor = '#0000ff';
    }
    
    const key = `${nodeId}-${socketData.name}-${isInput ? 'in' : 'out'}`;
    allSockets.set(key, socketEl);
    
    return socketEl;
}

function deleteNode(nodeEl) {
    const nodeId = nodeEl.dataset.id;
    
    // Kanten löschen, die mit diesem Node verbunden sind
    edges.filter(e => e.startEl.dataset.nodeId === nodeId || e.endEl.dataset.nodeId === nodeId)
            .forEach(deleteEdge);
            
    nodes = nodes.filter(n => n !== nodeEl);
    nodeEl.remove();
    
    allSockets.forEach((socketEl, key) => {
        if (socketEl.dataset.nodeId === nodeId) {
            allSockets.delete(key);
        }
    });

    drawEdges();
}

// --- EDGE RENDERING & LOGIC ---

function deleteEdge(edge) {
    if (edge.pathEl) {
        edge.pathEl.remove();
    }
    edges = edges.filter(e => e !== edge);
    console.log('Kante gelöscht.');
}

function createEdge(startSocketEl, endSocketEl) {
    const isDuplicate = edges.some(edge => (edge.startEl === startSocketEl && edge.endEl === endSocketEl));
    if (isDuplicate) return;

    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.className = 'edge-path'; 
    path.setAttribute('fill', 'none');
    path.setAttribute('stroke', startSocketEl.style.backgroundColor || '#f0f0f0');
    path.setAttribute('stroke-width', '3');
    
    const newEdge = {
        startEl: startSocketEl,
        endEl: endSocketEl,
        pathEl: path
    };
    
    edges.push(newEdge);
    edgeSVG.appendChild(path);
    
    path.addEventListener('click', (e) => {
        deleteEdge(newEdge);
        e.stopPropagation(); 
    });
    
    drawEdges();
}

function drawBezierPath(startPos, endPos) {
    const p1 = startPos;
    const p4 = endPos;
    
    const dx = Math.max(50, Math.abs(p4.x - p1.x) / 3);
    const offsetDirection = p1.x < p4.x ? 1 : -1;
    
    const p2 = { x: p1.x + dx * offsetDirection, y: p1.y };
    const p3 = { x: p4.x - dx * offsetDirection, y: p4.y };

    return `M${p1.x},${p1.y} C${p2.x},${p2.y} ${p3.x},${p3.y} ${p4.x},${p4.y}`;
}

function drawEdges() {
    const editorRect = editorContainer.getBoundingClientRect();
    
    edges.forEach(edge => {
        if (!edge.startEl || !edge.endEl) return;
        
        const startPos = getSocketAbsolutePosition(edge.startEl);
        const endPos = getSocketAbsolutePosition(edge.endEl);
        
        startPos.x -= editorRect.left;
        startPos.y -= editorRect.top;
        endPos.x -= editorRect.left;
        endPos.y -= editorRect.top;
        
        const d = drawBezierPath(startPos, endPos);
        edge.pathEl.setAttribute('d', d);
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

function areTypesCompatible(type1, type2) {
        if (type1 === type2) return true;
        if ((type1 === "float" && type2 === "int") || (type1 === "int" && type2 === "float")) return true;
        return false;
}

function checkAndCreateConnection(startSocket, targetSocket) {
    if (startSocket.dataset.nodeId === targetSocket.dataset.nodeId) return;
    
    const startIsInput = startSocket.dataset.isInput === 'true';
    const targetIsInput = targetSocket.dataset.isInput === 'true';

    if (startIsInput === targetIsInput) return; 
    
    const [outSocket, inSocket] = startIsInput ? [targetSocket, startSocket] : [startSocket, targetSocket];
    
    if (!areTypesCompatible(outSocket.dataset.type, inSocket.dataset.type)) {
        console.log(`❌ Verbindung ABGELEHNT: Typen inkompatibel (${outSocket.dataset.type} -> ${inSocket.dataset.type}).`);
        return;
    }
    
    createEdge(outSocket, inSocket);
}

// --- INTERACTION HANDLERS (ZWEI-KLICK) ---
// Die Interaktionslogik bleibt unverändert

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
        
        drawEdges(); 
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

        drawEdges();
        return;
    }

    if (state.isDraggingNode && state.draggedNode) {
        const nodeEl = state.draggedNode;
        
        nodeEl.nodeData.x = (e.clientX - state.offsetX - state.dragOffset.x) / state.scale;
        nodeEl.nodeData.y = (e.clientY - state.offsetY - state.dragOffset.y) / state.scale;

        nodeEl.style.left = `${nodeEl.nodeData.x}px`;
        nodeEl.style.top = `${nodeEl.nodeData.y}px`;
        drawEdges(); 
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

// --- SPEICHERN & LADEN LOGIK ---
const STORAGE_KEY = 'nodeGraphDataV4';

function saveGraph() {
    const data = {
        nodes: nodes.map(nodeEl => ({
            id: nodeEl.nodeData.id,
            name: nodeEl.nodeData.name,
            x: nodeEl.nodeData.x,
            y: nodeEl.nodeData.y,
            presetIndex: nodePresets.findIndex(p => p.name === nodeEl.nodeData.name)
        })),
        edges: edges.map(edge => ({
            startNodeId: edge.startEl.dataset.nodeId,
            startSocketName: edge.startEl.dataset.name,
            endNodeId: edge.endEl.dataset.nodeId,
            endSocketName: edge.endEl.dataset.name
        })),
        viewport: {
            offsetX: state.offsetX,
            offsetY: state.offsetY,
            scale: state.scale
        }
    };

    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
        console.log('Graph erfolgreich gespeichert!');
        saveBtn.textContent = '✅ Gespeichert!';
        setTimeout(() => saveBtn.textContent = '💾 Speichern', 1000);
    } catch (e) {
        console.error('Fehler beim Speichern:', e);
    }
}

/** Gibt true zurück, wenn erfolgreich geladen wurde, sonst false. */
function loadGraph() {
    try {
        const storedData = localStorage.getItem(STORAGE_KEY);
        if (!storedData) {
            console.log('Keine gespeicherten Daten gefunden.');
            return false;
        }

        const data = JSON.parse(storedData);
        
        // 1. Graph leeren
        nodes.forEach(n => n.remove());
        edges.forEach(e => e.pathEl.remove());
        nodes = [];
        edges = [];
        allSockets.clear();
        
        // 2. Nodes neu erstellen
        data.nodes.forEach(nodeData => {
            const preset = nodePresets[nodeData.presetIndex];
            if (preset) {
                createNodeElement({ ...preset }, nodeData.x, nodeData.y, nodeData.id);
            }
        });

        // 3. Edges (Kanten) neu erstellen
        data.edges.forEach(edgeData => {
            const startKey = `${edgeData.startNodeId}-${edgeData.startSocketName}-out`;
            const endKey = `${edgeData.endNodeId}-${edgeData.endSocketName}-in`;
            
            const startSocket = allSockets.get(startKey);
            const endSocket = allSockets.get(endKey);

            if (startSocket && endSocket) {
                // Muss immer von Output zu Input sein!
                const [outSocket, inSocket] = startSocket.dataset.isInput === 'true' ? [endSocket, startSocket] : [startSocket, endSocket];
                createEdge(outSocket, inSocket);
            } else {
                console.warn(`Socket für Kante nicht gefunden: ${startKey} -> ${endKey}`);
            }
        });
        
        // 4. Viewport-Zustand wiederherstellen
        if (data.viewport) {
            state.offsetX = data.viewport.offsetX;
            state.offsetY = data.viewport.offsetY;
            state.scale = data.viewport.scale;
        }

        loadBtn.textContent = '✅ Geladen!';
        setTimeout(() => loadBtn.textContent = '↩️ Laden', 1000);
        return true; 

    } catch (e) {
        console.error('Fehler beim Laden:', e);
        loadBtn.textContent = '❌ Fehler!';
        setTimeout(() => loadBtn.textContent = '↩️ Laden', 1000);
        return false;
    }
}

// --- INITIALIZATION (KORRIGIERT) ---

function init() {
    saveBtn.addEventListener('click', saveGraph);
    loadBtn.addEventListener('click', loadGraph);

    let loadedSuccessfully = false;
    
    // 1. Lade versuchen, falls Daten vorhanden sind
    if (localStorage.getItem(STORAGE_KEY)) {
        loadedSuccessfully = loadGraph(); 
    }
    
    // 2. Initialen Graphen erstellen, wenn Laden fehlschlägt oder keine Daten vorhanden sind
    if (!loadedSuccessfully) {
        console.log('Erstelle Initialgraphen.');
        // Sicherstellen, dass der Viewport zentriert ist
        state.offsetX = window.innerWidth / 4; 
        state.offsetY = window.innerHeight / 4; 
        state.scale = 1.0; 
        
        // Beispiel-Nodes erstellen
        createNodeElement(nodePresets[1], 300, 50); // Move Node
        createNodeElement(nodePresets[0], 50, 50); // Position (Outputs X, Y, Z)
        createNodeElement(nodePresets[2], 600, 50); // Start (Exec)
    }
    
    updateGraphTransform();
}

init();