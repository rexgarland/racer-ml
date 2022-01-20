const { dot, sigmoid } = require('./utils')

test('dot product', () => {
	expect(dot([1,2],[[0,0,1],[2,3,0]])).toEqual([4,6,1])
})

test('sigmoid', () => {
	expect(sigmoid(1)).toBeLessThan(1)
})