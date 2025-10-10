function downloadExcel(boardId, frameId, nodeId) {
    window.open("/get/board/" + boardId + "/frame/" + frameId + "/object/" + nodeId + "/excel", "_self")
    // fetch()
}

function populateNodes(boardId, frameId, nodes) {
    const startError = document.getElementById("start-error")
    startError.innerHTML = ""
    if (nodes.length == 0) {
        startError.innerText = "You don't have any nodes in this frame"
        return
    }

    const selectEl = document.getElementById("start")
    selectEl.innerHTML = ""
    let selectedNode = null
    for (const node of nodes) {
        if (selectedNode === null)
            selectedNode = node.id
        const option = document.createElement("option")
        option.value = node.id
        option.innerText = node.name
        selectEl.appendChild(option)
    }
    document.getElementById("select-start").style.display = "block"

    const runButton = document.getElementById("run")
    runButton.style.display = "block"
    runButton.onclick = () => {
        downloadExcel(boardId, frameId, selectedNode)
    }

    selectEl.onchange = () => {
        runButton.onclick = () => {
            downloadExcel(boardId, frameId, selectEl.value)
        }
    }
}

function populateFrames(boardId, frames) {
    const frameError = document.getElementById("frame-error")
    frameError.innerHTML = ""
    if (frames.length == 0) {
        frameError.innerText = "You don't have any frames in this board"
        return
    }

    const selectEl = document.getElementById("frame")
    selectEl.innerHTML = ""
    let selectedFrame = null
    for (const frame of frames) {
        if (selectedFrame === null)
            selectedFrame = frame.id
        const option = document.createElement("option")
        option.value = frame.id
        option.innerText = frame.name
        selectEl.appendChild(option)
    }
    document.getElementById("select-frame").style.display = "block"

    fetch("/get/board/" + boardId + "/frame/" + selectedFrame + "/objects").then(response => response.json()).then(nodes => populateNodes(boardId, selectedFrame, nodes))
    selectEl.onchange = () => {
        fetch("/get/board/" + boardId + "/frame/" + selectEl.value + "/objects").then(response => response.json()).then(nodes => populateNodes(boardId, selectEl.value, nodes))
    }
}

function populateBoards(boards) {
    const boardError = document.getElementById("board-error")
    boardError.innerHTML = ""
    if (boards.length == 0) {
        boardError.innerText = "You don't have any boards"
        return
    }

    const selectEl = document.getElementById("board")
    selectEl.innerHTML = ""
    let selectedBoard = null
    for (const board of boards) {
        if (selectedBoard === null)
            selectedBoard = board.id
        const option = document.createElement("option")
        option.value = board.id
        option.innerText = board.name
        selectEl.appendChild(option)
    }
    document.getElementById("select-board").style.display = "block"

    fetch("/get/board/" + selectedBoard + "/frames").then(response => response.json()).then(frames => populateFrames(selectedBoard, frames))
    selectEl.onchange = () => {
        fetch("/get/board/" + selectEl.value + "/frames").then(response => response.json()).then(frames => populateFrames(selectEl.value, frames))
    }
}

fetch("/get/boards").then(response => response.json()).then(populateBoards)