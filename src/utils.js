
function argMax(v) {
	var i = 0
	var m = v[0]
	for (var j=1; j<v.length; j++) {
		if (v[j]>m) {
			i = j
			m = v[j]
		}
	}
	return i
}

function randomlyChoose(arr) {
	var r = Math.random()
	var d = 1.0/arr.length;
	return arr[Math.floor(r/d)]
}

function randn() {
  let u = 0, v = 0;
  while(u === 0) u = Math.random(); //Converting [0,1) to (0,1)
  while(v === 0) v = Math.random();
  let num = Math.sqrt( -2.0 * Math.log( u ) ) * Math.cos( 2.0 * Math.PI * v );
  num = num / 10.0 + 0.5; // Translate to 0 -> 1
  if (num > 1 || num < 0) return randn() // resample between 0 and 1
  return num
}

function deepAbsMax(weights) {
	if (!weights.length) {
		return weights
	} else {
		return weights.map(deepAbsMax).reduce((a,v)=>Math.max(a,Math.abs(v)),0)
	}
}

function cloneDeep(weights) {
	if (!weights.length) {
		return weights
	} else {
		return weights.map(cloneDeep)
	}
}

function sigmoid(x) {
	return Math.exp(x)/(Math.exp(x)+1)
}

function dot(x,w) {
	// matrix multiply input |x| (1 x n) with |w| (n x m)
	var out = []
	for (var m = 0; m<w[0].length; m++) {
		var sum = 0
		for (var n=0; n<w.length; n++) {
			sum = sum + x[n]*w[n][m];
		}
		out.push(sum);
	}
	return out;
}

module.exports = {
	argMax,
	randomlyChoose,
	randn,
	deepAbsMax,
	cloneDeep,
	dot,
	sigmoid
}