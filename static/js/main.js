const fromCurrency = document.getElementById("from_currency");
const toCurrency = document.getElementById("to_currency");
const sourceSelect = document.getElementById("source");
const rateTypeGroup = document.getElementById("rate-type-group");
const rateTypeSelect = document.getElementById("rate_type");


// ==============================
// Nút đổi chiều tiền tệ
// ==============================
document.getElementById("swap-btn").addEventListener("click", function () {

    const temp = fromCurrency.value;

    fromCurrency.value = toCurrency.value;
    toCurrency.value = temp;

    updateRateType();
});

function updateCurrencyOptions() {
    const source = sourceSelect.value;

    const fromOptions = fromCurrency.querySelectorAll("option");
    const toOptions = toCurrency.querySelectorAll("option");

    // Frankfurter: hiện lại toàn bộ tiền tệ
    if (source !== "vietcombank") {
        fromOptions.forEach(option => {
            option.hidden = false;
        });

        toOptions.forEach(option => {
            option.hidden = false;
        });

        return;
    }

    // Vietcombank:
    // chỉ giữ VND + những ngoại tệ VCB thực sự hỗ trợ
    fromOptions.forEach(option => {
        const code = option.value;

        option.hidden =
            code !== "VND" &&
            !window.vcbCurrencies.includes(code);
    });


    // Nếu TỪ = VND
    // thì SANG chỉ được là ngoại tệ VCB hỗ trợ
    if (fromCurrency.value === "VND") {

        toOptions.forEach(option => {
            const code = option.value;

            option.hidden =
                code === "VND" ||
                !window.vcbCurrencies.includes(code);
        });

    } else {

        // Nếu TỪ = ngoại tệ
        // thì SANG chỉ được là VND
        toOptions.forEach(option => {
            option.hidden = option.value !== "VND";
        });

        toCurrency.value = "VND";
    }
}


// ==============================
// Cập nhật loại giao dịch VCB
// ==============================
function updateRateType() {

    const source = sourceSelect.value;
    const from = fromCurrency.value;
    const to = toCurrency.value;


    // Frankfurter không có Buy / Transfer / Sell
    if (source !== "vietcombank") {
        rateTypeGroup.style.display = "none";
        return;
    }


    // Vietcombank
    rateTypeGroup.style.display = "block";


    // VND -> Ngoại tệ
    // Ngân hàng BÁN ngoại tệ cho khách
    if (from === "VND" && to !== "VND") {

        rateTypeSelect.innerHTML = `
            <option value="sell">
                Bán (Sell)
            </option>
        `;

        return;
    }


    // Ngoại tệ -> VND
    // Ngân hàng MUA ngoại tệ của khách
    if (from !== "VND" && to === "VND") {

        rateTypeSelect.innerHTML = `
            <option value="transfer">
                Mua chuyển khoản
            </option>

            <option value="cash">
                Mua tiền mặt
            </option>
        `;

        return;
    }


    // Các trường hợp khác
    rateTypeSelect.innerHTML = `
        <option value="">
            Không áp dụng
        </option>
    `;
}


// Đổi nguồn tỷ giá
sourceSelect.addEventListener("change", function () {
    updateCurrencyOptions();
    updateRateType();
});

// Đổi tiền nguồn
fromCurrency.addEventListener("change", function () {
    updateCurrencyOptions();
    updateRateType();
});

// Đổi tiền đích
toCurrency.addEventListener("change", updateRateType);

// Chạy lần đầu khi trang được load
updateCurrencyOptions();
updateRateType();