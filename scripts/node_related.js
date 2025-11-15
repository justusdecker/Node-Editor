
let nodes = []; 
let edges = []; 
let allSockets = new Map(); 

const editorContainer = document.getElementById('editor-container');
const nodeGraph = document.getElementById('node-graph');
const edgeSVG = document.getElementById('edge-svg');
const saveBtn = document.getElementById('save-btn');
const loadBtn = document.getElementById('load-btn');


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
            { name: 'X', type: 'int', isOutput: true },
            { name: 'Y', type: 'int', isOutput: true }, 
            { name: 'Z', type: 'int', isOutput: true }
        ]
    }
];

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
    const inOut = nodeData.name;
    console.log(nodeData)

    const maxSockets = inOut.length;

    for (let i = 0; i < maxSockets; i++) {
        const data = inOut[i];
        
        const row = document.createElement('div');
        row.className = 'socket-row';
        const socket = createSocket(nodeElement, data, true);
        const nameSpan = document.createElement('span');

        // Input Socket
        if (data.isInput) {
            
            socket.class = 'socket input';
            socket.type = "float";
            socket.name = "Value In";
            row.appendChild(socket);
            row.appendChild(nameSpan);
            body.appendChild(row);
        }

        // Output Socket
        if (data.isOutput) {
            socket.class = 'socket output';
            socket.type = "float";
            socket.name = "Value In";

            row.appendChild(nameSpan);
            row.appendChild(socket);
        }
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

function init() {
    createNode(nodePresets[1], 300, 50);
    createNode(nodePresets[0], 50, 50);
}
init();