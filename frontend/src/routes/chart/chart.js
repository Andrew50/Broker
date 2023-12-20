import { math } from './math.js';

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
        this.margin = 30;

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
            this.#draw();
            
        } else {
            console.error('data is not an array');
        }
      
    }

    #getPixelBounds() {
        const { canvas, margin } = this;
        const bounds = {
            right: canvas.width - margin,
            left: margin,
            top: margin,
            bottom: canvas.height - margin

        }
        return bounds;
    }

    #getDataBounds() {
        //const dates = this.data.map(dataPoint => new Date(dataPoint[0]));
        const high = this.data.map(dataPoint => dataPoint[3]);
        const low = this.data.map(dataPoint => dataPoint[4]);

        // Find the minimum and maximum dates
        //const minX = new Date(Math.min(...dates.map(date => date.getTime())));
        //const maxX = new Date(Math.max(...dates.map(date => date.getTime())));
        const minX = 0;
        const maxX = this.data.length;
        const maxY = Math.max(...high);
        const minY = Math.min(...low);
            

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
        console.log(this.pixelBounds);
        console.log(this.dataBounds);
    }

   #drawData() {
       const { ctx, data, dataBounds, pixelBounds } = this;
       let i = 0;
       const width = (Math.abs(pixelBounds.left - pixelBounds.right)/data.length)
       for (const candleStick of data) {
            const pixelLoc = [
                math.remap(dataBounds.left, dataBounds.right, pixelBounds.left, pixelBounds.right, i),
                math.remap(dataBounds.top, dataBounds.bottom, pixelBounds.top, pixelBounds.bottom, candleStick[1]),
                math.remap(dataBounds.top, dataBounds.bottom, pixelBounds.top, pixelBounds.bottom, candleStick[2]),
                math.remap(dataBounds.top, dataBounds.bottom, pixelBounds.top, pixelBounds.bottom, candleStick[3]),
                math.remap(dataBounds.top, dataBounds.bottom, pixelBounds.top, pixelBounds.bottom, candleStick[4])
           ];
           i++;
           this.#drawCandle(ctx,pixelLoc,width - 1);
        }
   }

    #drawCandle(ctx, pixelLoc, width) {
        if (pixelLoc[1] < pixelLoc[4]) {
            ctx.fillStyle = 'green';
        }
        else {
            ctx.fillStyle = 'red';
        }
        //console.log(pixelLoc);  
        ctx.fillRect(pixelLoc[0] - width/2, (pixelLoc[1] + pixelLoc[4]) / 2, width, Math.abs(pixelLoc[1] - pixelLoc[4]));
        ctx.fillRect(pixelLoc[0] - width/6, (pixelLoc[2] + pixelLoc[3]) / 2, width/3, Math.abs(pixelLoc[2] - pixelLoc[3]));
        //ctx.fillRect(100, 100, 20, 20);
    }
   
   
}