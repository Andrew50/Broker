import { math } from './math.js';
export class chart2 {
    constructor(container, chart_data, options) {
        this.candleWidth = options.candleWidth;
        this.canvas = document.createElement('canvas')
        this.canvas.width = window.innerWidth - options.widthOffset;
        this.canvas.height = window.innerHeight;
        this.canvas.style = 'background-color:black;';
        this.canvas.requestFullscreen();
        container.appendChild(this.canvas);
        this.ctx = this.canvas.getContext("2d");
        this.margin = options.margin;
        this.prev;
        this.a = 0;
        this.wickWidth = 2;
        this.isDragging = false;
        this.xAxisOffset = 0;
        this.#addEventListener();
        this.Lines = 0;
        this.pixInt = 0;
        this.yScale = 0;
        this.cursorPos = {
            x: 0,
            y: 0
        };
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
        this.canvas.onmousedown = (evt) => {
            this.isDragging = true;
            this.prev = event.clientX;
        }
        this.canvas.onmousemove = (evt) => {
            this.cursorPos = {
                x: event.clientX,
                y: event.clientY
            };
            if (this.isDragging && event.clientX < this.canvas.width - this.margin) {
                const neww = event.clientX;
                if ((this.a + ((this.prev - event.clientX) / this.candleWidth)) < 0 && (this.data.length + (this.a) - Math.floor((this.pixelBounds.right) / this.candleWidth) + (this.prev - event.clientX) / this.candleWidth) >= -1) {
                    this.xAxisOffset = this.xAxisOffset - ((this.prev - neww) / this.candleWidth);
                    this.a = this.a + ((this.prev - neww) / this.candleWidth);
                }
                this.prev = neww;
                this.#draw(false);

            }
            else {
                this.isDragging = false;
                this.#draw(true);
            }
            
        }
        this.canvas.onmouseup = () => {
            this.isDragging = false;
        }
        this.canvas.onwheel = (evt) => {
            const newCandleWidth = (this.pixelBounds.right) / ((evt.deltaY / (this.candleWidth ^ .5)) + (this.pixelBounds.right) / (this.candleWidth));
            if ((this.data.length + (this.a) - Math.floor((this.pixelBounds.right) / newCandleWidth)) >= 0) {
                if (newCandleWidth > 1 && newCandleWidth < 81) {
                    this.candleWidth = newCandleWidth;//this.candleWidth = evt.deltaY / 50 + this.candleWidth
                }
                //this.candleWidth = newCandleWidth;//this.candleWidth = evt.deltaY / 50 + this.candleWidth
            }
            else{
                //display max candles
                //console.log()
                this.a = Math.ceil(this.a)
                this.candleWidth = ((this.pixelBounds.right) / (this.data.length + this.a));
            }

            this.#draw(false);
            this.Lines = 0;
            this.yScale = 0;

        }
    }

    #convertData(chart_data) {
        if (Array.isArray(chart_data)) {
            this.data = chart_data.map(obj => Object.values(obj));
            this.a = 0;
            this.candleWidth = 10; // calculate candle width if pixelbounds / data.length < 10
            this.#draw()
            console.log(this.data[this.data.length - 2])

        } else {
            console.error('data is not an array');
        }

    }

    #getPixelBounds() {
        const { canvas, margin } = this;
        const bounds = {
            right: canvas.width - margin + this.candleWidth,
            left: 0,
            top: 20,
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

    #draw(cursor) {
        const { ctx, canvas } = this;
        //clear area
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        //console.log(this.data.length + Math.ceil(this.a) - Math.floor((this.canvas.width - this.margin) / this.candleWidth));
        //console.log(this.data.length + Math.ceil(this.a));
        this.pixelBounds = this.#getPixelBounds();
        const dataSliced = this.data.slice(this.data.length + Math.ceil(this.a) - Math.floor((this.pixelBounds.right) / this.candleWidth), this.data.length + Math.ceil(this.a));
        this.dataBounds = this.#getDataBounds(dataSliced);
        let i = 0;

        for (const candleStick of dataSliced) {
            this.#drawData(i, candleStick);
            i++;
        }
        if (dataSliced.length > 0) {
            this.#drawAxes(dataSliced);
        }
        if (cursor) {
            this.#drawCursor();
        }
        
    }

    #drawData(i, candleStick) {
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
        ctx.fillRect(pixelLoc[0] - xOffset + this.candleWidth / 2 - this.wickWidth/2, ((pixelLoc[2] + pixelLoc[3]) - Math.abs(pixelLoc[2] - pixelLoc[3])) / 2, this.wickWidth, Math.abs(pixelLoc[2] - pixelLoc[3]));


    }
    // abs(this.a + this.a*num lines passed)

    #drawAxes(dataSliced) {
        this.ctx.save();
        this.ctx.strokeStyle = 'white';
        this.ctx.globalCompositeOperation = 'destination-over';
        this.ctx.globalAlpha = 0.5;
        this.ctx.beginPath();

        const xOffset = Math.abs(this.a - Math.floor(this.a)) * this.candleWidth
        let xAxisOffset = Math.abs(this.a) - Math.floor(dataSliced.length / 5) * this.Lines;

        if (Math.floor(xAxisOffset) > Math.floor(dataSliced.length / 5)) {
            
            this.Lines = this.Lines + 1;
            xAxisOffset = Math.abs(this.a) - Math.floor(dataSliced.length / 5) * this.Lines;
            
        }
        else if (Math.floor(xAxisOffset) < 0) {
            this.Lines = this.Lines - 1;
            xAxisOffset = Math.abs(this.a) - Math.floor(dataSliced.length / 5) * this.Lines;

        }
        for (let i = xAxisOffset; i < dataSliced.length + 1; i += Math.floor(dataSliced.length / 5)) {
            const pixelLoc = math.remap(this.dataBounds.left, this.dataBounds.right, this.pixelBounds.left, this.pixelBounds.right, Math.floor(i) + 0.5);
            console.log(i);
            if (i < dataSliced.length) {
                this.#drawText(dataSliced[Math.floor(i)][0], [pixelLoc - xOffset - this.wickWidth / 2, this.pixelBounds.bottom + this.margin / 2], this.margin * 0.5);
            }
            this.ctx.beginPath();
            this.ctx.moveTo(pixelLoc - xOffset - this.wickWidth / 2, this.pixelBounds.bottom);
            this.ctx.lineTo(pixelLoc - xOffset - this.wickWidth / 2, this.pixelBounds.top);
            this.ctx.stroke();
        }
        // yAxis
        this.ctx.clearRect(this.canvas.width - this.margin, 0, this.margin, this.canvas.height);
        
        if (this.yScale > (this.dataBounds.top - this.dataBounds.bottom)/7 || this.yScale < (this.dataBounds.top - this.dataBounds.bottom)/13 ) {
            this.yScale = this.#sigFigs(Math.floor((this.dataBounds.top - this.dataBounds.bottom) / 10), 2);
            this.refrencePrice = this.dataBounds.bottom;
        }
        //set refernce and price can render bellow or above as needed
        // convert to lines bellow and then multiply by the y.scale
        //Math.ceil((this.refrencePrice - this.dataBounds.bottom)/this.yScale) * this.yScale
        console.log(Math.ceil((this.refrencePrice - this.dataBounds.bottom) / this.yScale) * this.yScale);
        for (let i = this.refrencePrice - Math.ceil((this.refrencePrice - this.dataBounds.bottom) / this.yScale) * this.yScale; i < (this.dataBounds.top); i += this.yScale) {
            const pixelLoc = math.remap(this.dataBounds.top, this.dataBounds.bottom, this.pixelBounds.top, this.pixelBounds.bottom, i);
            this.#drawText(this.#sigFigs(i, 3), [this.canvas.width - 2, pixelLoc], this.margin * 0.5);
            this.ctx.beginPath();
            this.ctx.lineWidth = 1;
            this.ctx.moveTo(this.pixelBounds.left, pixelLoc);
            this.ctx.lineTo(this.canvas.width - this.margin, pixelLoc);
            this.ctx.stroke();
        }

        this.ctx.restore();

    }

    #drawCursor() {
        this.ctx.save();
        this.ctx.strokeStyle = 'white';
        console.log(this.cursorPos);
        const xOffset = Math.abs(this.a - Math.floor(this.a)) * this.candleWidth;
        const roundCandle = Math.round(math.remap(this.pixelBounds.left, this.pixelBounds.right, this.dataBounds.left, this.dataBounds.right, this.cursorPos.x - this.candleWidth/2 + xOffset));
        const roundCandlePos = math.remap(this.dataBounds.left, this.dataBounds.right, this.pixelBounds.left, this.pixelBounds.right, roundCandle);
        const price = math.remap(this.pixelBounds.top, this.pixelBounds.bottom, this.dataBounds.top, this.dataBounds.bottom, this.cursorPos.y);
        this.ctx.beginPath();
        this.ctx.moveTo(this.pixelBounds.left, this.cursorPos.y);
        this.ctx.lineTo(this.canvas.width - this.margin, this.cursorPos.y);
        this.ctx.stroke();

        this.ctx.beginPath();
        this.ctx.moveTo(roundCandlePos - xOffset + this.candleWidth / 2 , this.pixelBounds.bottom);
        this.ctx.lineTo(roundCandlePos - xOffset + this.candleWidth / 2 , this.pixelBounds.top);
        this.ctx.stroke();
        this.ctx.restore();

        this.ctx.clearRect(this.canvas.width - this.margin, this.cursorPos.y - 6, this.margin, 12);
        this.#drawText(this.#sigFigs(price, 3), [this.canvas.width - 2, this.cursorPos.y], this.margin * 0.5);
    }

    #drawText(text, loc, size) {
        const ctx = this.ctx
        ctx.textAlign = 'right';
        ctx.textBaseline = 'middle';
        ctx.font = "bold " + size + "px Courier";
        ctx.fillStyle = 'grey';
        ctx.fillText(text, ...loc);

    }

    #sigFigs(n, sig) {
        if (n === 0)
            return 0
        var mult = Math.pow(10,
            sig - Math.floor(Math.log(n < 0 ? -n : n) / Math.LN10) - 1);
        return Math.round(n * mult) / mult;
    }


}