import {math} from './math.js';
import {chart} from './class.js';
import {toDT} from '../store.js';

chart.prototype.drawAxes = function(dataSliced) {
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
        if (i < dataSliced.length) {
            const arg = this.isIntraday() ? 3 : 1;
            this.drawAxesText(toDT(dataSliced[Math.floor(i)][0],arg), [pixelLoc - xOffset - this.wickWidth / 2, this.pixelBounds.bottom + this.margin / 2], this.margin * 0.5);
        }
        this.ctx.beginPath();
        this.ctx.moveTo(pixelLoc - xOffset - this.wickWidth / 2, this.pixelBounds.bottom);
        this.ctx.lineTo(pixelLoc - xOffset - this.wickWidth / 2, this.pixelBounds.top);
        this.ctx.stroke();
    }
    // yAxis
    this.ctx.clearRect(this.canvas.width - this.margin, 0, this.margin, this.canvas.height);
    if (this.yScale > (this.dataBounds.top - this.dataBounds.bottom)/7 || this.yScale < (this.dataBounds.top - this.dataBounds.bottom)/13 ) {
        this.yScale = math.sigFigs(Math.ceil((this.dataBounds.top - this.dataBounds.bottom) / 10), 2);
        this.refrencePrice = this.dataBounds.bottom;
    }
    //set refernce and price can render bellow or above as needed
    // convert to lines bellow and then multiply by the y.scale
    //Math.ceil((this.refrencePrice - this.dataBounds.bottom)/this.yScale) * this.yScale
    for (let i = this.refrencePrice - Math.floor((this.refrencePrice - this.dataBounds.bottom) / this.yScale) * this.yScale; i < (this.dataBounds.top * (this.pixelBounds.top - this.pixelBounds.bottomC) / (this.pixelBounds.topC - this.pixelBounds.bottomC)); i += this.yScale) {
        const pixelLoc = math.remap(this.dataBounds.top, this.dataBounds.bottom, this.pixelBounds.topC, this.pixelBounds.bottomC, i);
        this.drawAxesText(math.sigFigs(i, 3), [this.canvas.width - 2, pixelLoc], this.margin * 0.5);
        this.ctx.beginPath();
        this.ctx.lineWidth = 1;
        this.ctx.moveTo(this.pixelBounds.left, pixelLoc);
        this.ctx.lineTo(this.canvas.width - this.margin, pixelLoc);
        this.ctx.stroke();
    }
    this.ctx.restore();
}


chart.prototype.drawAxesText = function(text, loc, size)  {
    const ctx = this.ctx
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    ctx.font = "bold " + size + "px Courier";
    ctx.fillStyle = 'grey';
    ctx.fillText(text, ...loc);
}

