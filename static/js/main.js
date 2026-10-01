// Nút đổi chiều tiền tệ
document.getElementById("swap-btn").addEventListener("click", function () {
    const fromCurrency = document.getElementById("from_currency");
    const toCurrency = document.getElementById("to_currency");

    const temp = fromCurrency.value;

    fromCurrency.value = toCurrency.value;
    toCurrency.value = temp;
});


// Nút chuyển đổi
document.getElementById("convert-btn").addEventListener("click", function () {
    const amountInput = document.getElementById("amount");
    const from = document.getElementById("from_currency").value;
    const to = document.getElementById("to_currency").value;
    const resultBox = document.getElementById("result");

    const amount = Number(amountInput.value);

    if (!amount || amount <= 0) {
        resultBox.innerHTML = `
            <p>Vui lòng nhập số tiền hợp lệ.</p>
        `;
        return;
    }

    const rate = Number(resultBox.dataset.rate);
    const date = resultBox.dataset.date;

    if (from === "USD" && to === "VND") {
        const result = amount * rate;

        resultBox.innerHTML = `
            <p>
                ${amount.toLocaleString()} ${from}
                =
                <strong>${result.toLocaleString()} ${to}</strong>
            </p>

            <p>
                Tỷ giá: 1 ${from} = ${rate.toLocaleString()} ${to}
            </p>

            <p>
                Ngày cập nhật: ${date}
            </p>
        `;
    } else {
        resultBox.innerHTML = `
            <p>
                ${amount.toLocaleString()} ${from}
                → ${to}
            </p>

            <p>
                Chức năng này sẽ được kết nối với backend.
            </p>
        `;
    }
});