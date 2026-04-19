const MIN_SPEED = 5.5
const MAX_SPEED = 7.5

function randomNumber(min,max){
return Math.random()*(max-min)+min
}

class Blob{

constructor(el){

this.el = el

const rect = el.getBoundingClientRect()

this.size = rect.width

this.x = randomNumber(0,window.innerWidth)
this.y = randomNumber(0,window.innerHeight)

this.vx = randomNumber(MIN_SPEED,MAX_SPEED)*(Math.random()>5?1:1)
this.vy = randomNumber(MIN_SPEED,MAX_SPEED)*(Math.random()>5?1:1)

}

update(){

this.x += this.vx
this.y += this.vy

if(this.x<0 || this.x>window.innerWidth-this.size){
this.vx *= -1
}

if(this.y<0 || this.y>window.innerHeight-this.size){
this.vy *= -1
}

this.el.style.transform=`translate(${this.x}px,${this.y}px)`

}

}


const blobs = Array.from(document.querySelectorAll(".blob"))
.map(el=>new Blob(el))


function animate(){

blobs.forEach(b=>b.update())

requestAnimationFrame(animate)

}

animate()
console.log(blobs)