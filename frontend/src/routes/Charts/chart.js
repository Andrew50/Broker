export class chart {
    constructor(container, data, options) {
        this.data = data;

        this.axesLables = options.axesLabels;
        this.styles = options.styles;

        this.canvas = document.createElement('canvas')
        this.canvas.width = options.size;
        this.canvas.height = options.size;
        this.canvas.style = 'background-color:black;';
        container.appendChild(this.canvas);

        this.ctx = this.canvas.getContext("2d");
        this.margin = options.size * .1;

        this.pixelBounds = this.#getPixelBounds();
        this.dataBounds = this.#getDataBounds();

        this.#draw();

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
        const { data } = this;
        const x = data.map(s => s.point[0]);
        const y = data.map(s => s.point[1]);
        const minX = math.min(...x);
        const maxX = math.max(...x);
        const minY = math.min(...y);
        const maxY = math.max(...y);
        const bounds = {
            left: minX,
            right: maxX,
            top: maxY,
            bottom: minY
        }
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