export class chart {
    constructor(container, chart_data, options) {
        this.axesLables = options.axesLabels;
        this.styles = options.styles;

        this.canvas = document.createElement('canvas')
        this.canvas.width = window.innerWidth - options.widthOffset;
        this.canvas.height = window.innerHeight - options.heightOffset;
        this.canvas.style = 'background-color:black;';
        container.appendChild(this.canvas);

        this.ctx = this.canvas.getContext("2d");
        this.margin = options.size * .1;

       // this.#draw();

    }

    updateData(chart_data) {
       this.#convertData(chart_data);
    }

    #convertData(chart_data) {
        if (Array.isArray(chart_data)) {
            const flattenedData = chart_data.map(obj => Object.values(obj));
            this.data = flattenedData;
            console.log(this.data);
            this.pixelBounds = this.#getPixelBounds();
            this.dataBounds = this.#getDataBounds();
            
        } else {
            console.error('data is not an array');
        }
      
    }

    #getPixelBounds() {
        const { canvas, margin } = this;
        const bounds = {
            left: canvas.width - margin,
            right: margin,
            top: margin,
            bottom: canvas.height - margin

        }
        return bounds;
    }

    #getDataBounds() {
        const dates = this.data.map(dataPoint => new Date(dataPoint[0]));
        const high = this.data.map(dataPoint => dataPoint[3]);
        const low = this.data.map(dataPoint => dataPoint[4]);

        // Find the minimum and maximum dates
        const minX = new Date(Math.min(...dates.map(date => date.getTime())));
        const maxX = new Date(Math.max(...dates.map(date => date.getTime())));
        const maxY = Math.max(...high);
        const minY = Math.min(...low);
            

        const bounds = {
            left: minX,
            right: maxX,
            top: maxY,
            bottom: minY
        }
        console.log(bounds);

        return bounds;
    }

    #draw() {
        const { ctx, canvas } = this;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        this.#drawData();
    }

    #drawData() {
        const { ctx, data, dataBounds, pixleBounds } = this;
        for (const candleStick of data) {

        }
    }
    
}