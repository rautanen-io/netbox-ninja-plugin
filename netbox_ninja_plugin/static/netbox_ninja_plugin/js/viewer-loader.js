function updateMxGraphData(configs) {

    for (const config of configs) {

        src = config.viewerScriptUrl;
        xmlData = config.xmlData;
        editUrl = config.editUrl;
        mxgraphContainerId = config.mxgraphContainerId;
    
        const mxgraphContainer = document.getElementById(mxgraphContainerId);
        const graphDiv = document.createElement('div');
    
        graphDiv.setAttribute('class', 'mxgraph');
        graphDiv.setAttribute('style', 'max-width:100%; max-height:100%; border:5px solid transparent;');
    
        const data = {
            highlight: '#0000ff',
            nav: false,
            resize: true,
            toolbar: 'zoom lightbox',
            edit: editUrl,
            xml: xmlData,
        };
        graphDiv.setAttribute('data-mxgraph', JSON.stringify(data));
        mxgraphContainer.appendChild(graphDiv);

        const mxscript = document.createElement('script');
        mxscript.type = 'text/javascript';
        mxscript.src = src;
        mxgraphContainer.appendChild(mxscript);
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const configs = window.NINJA_CONFIGS;
    updateMxGraphData(configs);
}, false);
