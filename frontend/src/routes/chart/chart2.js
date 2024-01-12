import { math } from './math.js';
export class chart2 {
    constructor(container, chart_data, options) {
        this.candleWidth = options.candleWidth;
        this.canvas = document.createElement('canvas')
        this.canvas.width = window.innerWidth - options.widthOffset;
        this.canvas.height = window.innerHeight - options.heightOffset;
        this.canvas.style = 'background-color:black;';
        container.appendChild(this.canvas);
        this.ctx = this.canvas.getContext("2d");
        this.margin = options.margin;
        this.prev;
        this.a = 0;
        this.wickWidth = 2;
        this.isDragging = false;
        this.#addEventListener();

        // this.#draw();
    }

    updateData(chart_data) {
        this.#convertData(chart_data);
    }
    updateInnerWidth(innerWidth) {
        this.canvas.width = innerWidth - options.widthOffset;
        console.log(innerWidth);
        this.#draw();
    }
    updateInnerHeight(innerHeight) {
        this.canvas.height = innerHeight - options.heightOffset;
        this.#draw();
    }

    #addEventListener() {
        /*this.canvas.addEventListener("mousedown", function (event) {
            this.isDragging = true;
            this.prev = event.clientX;
        });

        this.canvas.addEventListener("mousemove", function (event) {
            if (this.isDragging) {
                console.log(this.candleWidth);
                //this.a = this.a + ((this.prev - event.clientX) / 900);
                //this.#draw();
                console.log("Mouse at: X=" + event.clientX + ", Y=" + event.clientY);
            }
        });

        this.canvas.addEventListener("mouseup", function (event) {
            this.isDragging = false;
        });
        */
        this.canvas.onmousedown = (evt) => {
            this.isDragging = true;
            this.prev = event.clientX;
        }
        this.canvas.onmousemove = (evt) => {
            if (this.isDragging && (this.a + this.data.length + ((this.prev - event.clientX) / this.candleWidth)) <= this.data.length) {
                //console.log(this.candleWidth);
                this.a = this.a + ((this.prev - event.clientX) / this.candleWidth);
                this.prev = event.clientX;
                this.#draw();
                //console.log("Mouse at: X=" + event.clientX + ", Y=" + event.clientY);
            }
        }
        this.canvas.onmouseup = () => {
            this.isDragging = false;
        }
        this.canvas.onwheel = (evt) => {
            this.candleWidth = this.candleWidth + evt.deltaY/10;
            if (this.candleWidth < 1) {
                this.candleWidth = 1;
                this.wickWidth = 1;
            }
            else if (this.candleWidth > 40) {
                this.candleWidth = 40;
            }
            else {
                this.wickWidth = 2;
            }
            
            this.#draw();
        }
    }

    #convertData(chart_data) {
        if (Array.isArray(chart_data)) {
           
            this.data = chart_data.map(obj => Object.values(obj));
            //this.data = flattenedData.slice(flattenedData.length - b, flattenedData.length - a);
            //this.data = flattenedData;
            //console.log(this.data);
            //this.pixelBounds = this.#getPixelBounds();
            //this.dataBounds = this.#getDataBounds();
                
            this.#draw();

        } else {
            console.error('data is not an array');
        }

    }

    #getPixelBounds() {
        const { canvas, margin } = this;
        const bounds = {
            right: canvas.width - this.candleWidth,
            left: 0,
            top: 0,
            bottom: canvas.height - margin,

        }
        return bounds;
    }

    #getDataBounds(dataSliced) {
        //const dates = this.data.map(dataPoint => new Date(dataPoint[0]));
        const high = dataSliced.map(dataPoint => dataPoint[2]);
        const low = dataSliced.map(dataPoint => dataPoint[3]);

        // Find the minimum and maximum dates
        //const minX = new Date(Math.min(...dates.map(date => date.getTime())));
        //const maxX = new Date(Math.max(...dates.map(date => date.getTime())));
        const minX = 0;
        const maxX = dataSliced.length;
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
        //clear area
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        const dataSliced = this.data.slice(this.data.length + Math.ceil(this.a) - Math.ceil(canvas.width / this.candleWidth), this.data.length + Math.ceil(this.a));
        //console.log(Math.ceil(this.a) - Math.ceil(canvas.width / this.candleWidth));
        //console.log(Math.ceil(this.a));
        //const dataSliced = this.data.slice(0,50);

        // get bounds
        this.pixelBounds = this.#getPixelBounds();
        this.dataBounds = this.#getDataBounds(dataSliced);
        //
        //console.log(this.pixelBounds);
        //console.log(this.dataBounds);
        let i = 0;
        //console.log(dataSliced);
        for (const candleStick of dataSliced) {
            this.#drawData(i , candleStick);
            i++;
        }
        this.#drawAxes();
    }

    #drawData(i,candleStick){
        const { ctx, data, dataBounds, pixelBounds } = this;
        const pixelLoc = [
            math.remap(dataBounds.left, dataBounds.right, pixelBounds.left, pixelBounds.right, i),
            math.remap(dataBounds.top, dataBounds.bottom, pixelBounds.top, pixelBounds.bottom, candleStick[1]),
            math.remap(dataBounds.top, dataBounds.bottom, pixelBounds.top, pixelBounds.bottom, candleStick[2]),
            math.remap(dataBounds.top, dataBounds.bottom, pixelBounds.top, pixelBounds.bottom, candleStick[3]),
            math.remap(dataBounds.top, dataBounds.bottom, pixelBounds.top, pixelBounds.bottom, candleStick[4])
        ];
        if (pixelLoc[1] < pixelLoc[4]) {
            ctx.fillStyle = 'red';
        }
        else {
            ctx.fillStyle = 'green';
        }
        
        const xOffset = Math.abs(this.a - Math.floor(this.a)) * this.candleWidth;
        //const xOffset = 0;
        
        ctx.fillRect(pixelLoc[0] - xOffset, ((pixelLoc[1] + pixelLoc[4]) - Math.abs(pixelLoc[1] - pixelLoc[4])) / 2, this.candleWidth, Math.abs(pixelLoc[1] - pixelLoc[4]));
        ctx.fillRect(pixelLoc[0] - xOffset + this.candleWidth / 2 - 1 , ((pixelLoc[2] + pixelLoc[3]) - Math.abs(pixelLoc[2] - pixelLoc[3])) / 2, this.wickWidth, Math.abs(pixelLoc[2] - pixelLoc[3]));
        
        
    }

    #drawAxes() {
        this.#drawText('X Axis', [this.canvas.width / 2, this.canvas.height - this.margin / 2], this.margin);
        this.ctx.clearRect(this.canvas.width - this.margin, 0, this.margin, this.canvas.height);
        //console.log(Math.ceil(this.dataBounds.bottom));
        //console.log(Math.floor(this.dataBounds.top));
        //console.log(Math.floor((this.dataBounds.top - this.dataBounds.bottom) / 10));
        for (let i = Math.ceil(this.dataBounds.bottom); i < Math.floor(this.dataBounds.top); i += Math.floor((this.dataBounds.top - this.dataBounds.bottom) / 10)) {
            const pixelLoc = math.remap(this.dataBounds.top, this.dataBounds.bottom, this.pixelBounds.top, this.pixelBounds.bottom, i);
            this.#drawText(i, [this.canvas.width - 2, pixelLoc], this.margin * 0.5);
            this.ctx.beginPath();
            this.ctx.strokeStyle = 'white';
            this.ctx.moveTo(this.pixelBounds.left, pixelLoc);
            this.ctx.lineTo(this.pixelBounds.right - this.margin, pixelLoc);
            this.ctx.stroke();
        }
        

    }

    #drawText(text,loc,size) {
        const ctx = this.ctx

        ctx.textAlign = 'right';
        ctx.textBaseline = 'middle';
        ctx.font = "bold " + size + "px Courier";
        ctx.fillStyle = 'grey';
        ctx.fillText(text, ...loc);
    
    }

    
}
