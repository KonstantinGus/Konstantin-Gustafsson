const calculateButton = document.getElementById('calculateButton');
const outputDiv = document.getElementById('output');
const ctx = document.getElementById('functionChart').getContext('2d');
let chart;

calculateButton.addEventListener('click', () => {
    const functionInput = document.getElementById('functionInput').value;
    const startX = parseFloat(document.getElementById('startX').value);
    const endX = parseFloat(document.getElementById('endX').value);
    const stepX = parseFloat(document.getElementById('stepX').value);
    const scaleY = parseFloat(document.getElementById('scaleY').value);


    outputDiv.innerHTML = "";


    if (!functionInput || isNaN(startX) || isNaN(endX) || isNaN(stepX) || isNaN(scaleY)) {
        outputDiv.innerText = "Fill in all fields";
        return;
    }

    if (startX >= endX) {
        outputDiv.innerText = "End must be bigger or equal to start";
        return;
    }

    if (stepX <= 0) {
        outputDiv.innerText = "Step cant be 0";
        return;
    }

    try {
        const xValuesForPlot = [];
        const yValuesForPlot = [];
        const xValuesForOutput = [];
        const yValuesForOutput = [];
        let outputText = "<p><strong>Calculated Values:</strong></p>";

        const plotStep = Math.min(stepX / 10, 0.01);

        with (Math) {
            for (let x = startX; x <= endX; x += plotStep) {
                const y = eval(functionInput) * scaleY;
                xValuesForPlot.push(x);
                yValuesForPlot.push(y);
            }

            for (let x = startX; x <= endX; x += stepX) {
                const y = eval(functionInput) * scaleY;
                xValuesForOutput.push(x);
                yValuesForOutput.push(y);
                outputText += `f(${x}) = ${y}<br>`;
            }
        }

        outputDiv.innerHTML = outputText;

        if (chart) chart.destroy();




        chart = new Chart(ctx, {
            type: "line",
            data: {
                labels: xValuesForPlot,
                datasets: [
                    {
                        label: `f(x) = ${functionInput}`,
                        data: yValuesForPlot,
                        borderColor: "blue",
                        borderWidth: 0.1,
                        fill: false,
                    },
                ],
            },
            options: {
                responsive: true,
                scales: {
                    x: { title: { display: true, text: "x" } },
                    y: { title: { display: true, text: "f(x)" } },
                },
            },
        });
    } catch (error) {
        outputDiv.innerText = "Bad function!";
    }
});
