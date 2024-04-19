//class.js 
export class chart {
    constructor(canvas, options) {
        /*this.container = container;
        this.candleWidth = this.defaultCandleWidth;
        this.canvas = document.createElement('canvas')
        this.canvas.style = `
        background-color:black; cursor:crosshair;
        'overflow:hidden;
        `
        //        this.canvas.requestFullscreen();
        container.appendChild(this.canvas);
        //        */
        this.candleWidth = options.defaultCandleWidth;
        this.canvas = canvas;
        this.ctx = this.canvas.getContext("2d");
        this.margin = options.margin;
        this.prev, this.ticker, this.i, this.nextT, this.pm, this.currentPrice;
        this.a = 0;
        this.wickWidth = 2;
        this.isDragging = false;
        this.xAxisOffset = 0;
        this.Lines = 0;
        this.pixInt = 0;
        this.yScale = 0;
        this.dataRateLimit = 1000;
        this.dataOffCooldown = true;
        this.cursorPos = {
            x: 0,
            y: 0
        };
        this.queryValid = false;
        this.addEventListener();
    }

    resetX(){
        this.xAxisOffset = 0;
        this.a = 0;
        this.draw();
    }

    resetView(){
        this.candleWidth = this.defaultCandleWidth;
        this.resetX();

    }

    updateInnerWidth(innerWidth) {
        this.canvas.width = innerWidth - options.widthOffset;
        this.draw();
    }

    updateInnerHeight(innerHeight) {
        this.canvas.height = innerHeight - options.heightOffset;
        this.draw();
    }

    addEventListener() {
        this.canvas.onmousedown = (evt) => {
            if (this.queryValid == false) {
                return;
            }
            this.isDragging = true;
            this.prev = evt.clientX;
        }
        this.canvas.onmousemove = (evt) => {
            if (this.queryValid == false) {
                return;
            }
            this.cursorPos = {
                x: evt.clientX,
                y: evt.clientY
            };
            if (this.isDragging){// && evt.clientX < this.canvas.width - this.margin) {
                const neww = evt.clientX;
                const a1 = (this.a + ((this.prev - evt.clientX) / this.candleWidth));
                const a2 = (this.data.length + (this.a) - Math.floor((this.pixelBounds.right) / this.candleWidth) + (this.prev - evt.clientX) / this.candleWidth);
                //const a2 = Math.ceil(this.a) - Math.floor((this.pixelBounds.right) / this.candleWidth)
                if (a1 < -1 && a2 >= -1) {
                //if (a2 < 0) {
                    this.xAxisOffset = this.xAxisOffset - ((this.prev - neww) / this.candleWidth);
                    this.a = this.a + ((this.prev - neww) / this.candleWidth);
                }
                this.prev = neww;
                this.draw(false);
                this.checkData();
            }
            else {
                this.isDragging = false;
                this.draw(true);
            }
            
        }
        this.canvas.onmouseup = () => {
            this.isDragging = false;
        }
        this.canvas.onwheel = (evt) => {
            if (this.queryValid == false) {
                return;
            }

            const newCandleWidth = (this.pixelBounds.right) / ((evt.deltaY / (this.candleWidth ^ .5)) + (this.pixelBounds.right) / (this.candleWidth));
            if ((this.data.length + (this.a) - Math.floor((this.pixelBounds.right) / newCandleWidth)) >= 0) {
                if (newCandleWidth > 1 && newCandleWidth < 81) {
                    this.candleWidth = newCandleWidth;//this.candleWidth = evt.deltaY / 50 + this.candleWidth
                }
                //this.candleWidth = newCandleWidth;//this.candleWidth = evt.deltaY / 50 + this.candleWidth
                this.checkData();
            }
            else{
                //display max candles
                this.a = Math.ceil(this.a)
                this.candleWidth = ((this.pixelBounds.right) / (this.data.length + this.a));
            }
            this.draw(false);
            //this.Lines = 0;
            //this.yScale = 0;
        }
        this.canvas.onmouseleave = () => {
            this.isDragging = false;
        }
        document.onkeydown = (evt) => {
            if (evt.altKey && evt.key === 'r'){
                evt.preventDefault();
                this.resetView();
            }
        }
    }
}
