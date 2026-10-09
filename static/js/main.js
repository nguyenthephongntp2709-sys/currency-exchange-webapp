const fromCurrency = document.getElementById("from_currency");
const toCurrency = document.getElementById("to_currency");
const sourceSelect = document.getElementById("source");
const rateTypeGroup = document.getElementById("rate-type-group");
const rateTypeSelect = document.getElementById("rate_type");
const swapButton = document.getElementById("swap-btn");

// Giữ loại mua đã chọn sau khi submit.
// Khi đổi chiều sang Sell rồi quay lại, vẫn nhớ loại mua này.
let selectedBuyType =
    rateTypeSelect.dataset.selected === "cash"
        ? "cash"
        : "transfer";

// Nếu HTML có truyền danh sách ngoại tệ VCB thì dùng để lọc.
// Nếu chưa có, vẫn cho giao diện hoạt động;
// backend sẽ kiểm tra ngoại tệ có được hỗ trợ hay không.
const vcbCurrencies = Array.isArray(window.vcbCurrencies)
    ? new Set(window.vcbCurrencies)
    : null;


// ==========================================
// LỌC CÁC LỰA CHỌN TIỀN TỆ
// ==========================================

function setCurrencyOptions(select, isAllowed) {
    for (const option of select.options) {
        const allowed = isAllowed(option.value);

        option.hidden = !allowed;
        option.disabled = !allowed;
    }

    // Nếu lựa chọn hiện tại không còn phù hợp,
    // chuyển sang lựa chọn hợp lệ đầu tiên.
    const currentOption = select.selectedOptions[0];

    if (!currentOption || currentOption.disabled) {
        const firstAllowed = Array.from(select.options).find(
            option => !option.disabled
        );

        select.value = firstAllowed ? firstAllowed.value : "";
    }
}

function isVcbForeignCurrency(code) {
    return (
        code !== "VND" &&
        (!vcbCurrencies || vcbCurrencies.has(code))
    );
}

function updateCurrencyOptions() {
    // Frankfurter: sử dụng toàn bộ danh sách tiền tệ.
    if (sourceSelect.value !== "vietcombank") {
        setCurrencyOptions(fromCurrency, () => true);
        setCurrencyOptions(toCurrency, () => true);
        return;
    }

    // Vietcombank: tiền nguồn là VND hoặc ngoại tệ.
    setCurrencyOptions(
        fromCurrency,
        code => code === "VND" || isVcbForeignCurrency(code)
    );

    if (fromCurrency.value === "VND") {
        // VND -> ngoại tệ
        setCurrencyOptions(toCurrency, isVcbForeignCurrency);
    } else {
        // Ngoại tệ -> VND
        setCurrencyOptions(
            toCurrency,
            code => code === "VND"
        );
    }
}


// ==========================================
// HIỂN THỊ LOẠI GIAO DỊCH VIETCOMBANK
// ==========================================

function updateRateType() {
    const isVietcombank =
        sourceSelect.value === "vietcombank";

    // Frankfurter: ẩn và không gửi rate_type trong form.
    rateTypeGroup.style.display =
        isVietcombank ? "flex" : "none";

    rateTypeSelect.disabled = !isVietcombank;

    if (!isVietcombank) {
        return;
    }

    const from = fromCurrency.value;
    const to = toCurrency.value;

    // Xóa các option cũ trước khi tạo lại.
    rateTypeSelect.replaceChildren();

    if (from === "VND" && to !== "VND" && to !== "") {
        // Ngân hàng bán ngoại tệ cho khách.
        rateTypeSelect.add(
            new Option("Bán (Sell)", "sell")
        );

        rateTypeSelect.value = "sell";
        return;
    }

    if (from !== "VND" && from !== "" && to === "VND") {
        // Ngân hàng mua ngoại tệ của khách.
        rateTypeSelect.add(
            new Option("Mua chuyển khoản", "transfer")
        );

        rateTypeSelect.add(
            new Option("Mua tiền mặt", "cash")
        );

        // Giữ lại loại mua đã chọn.
        rateTypeSelect.value = selectedBuyType;
        return;
    }

    rateTypeSelect.add(
        new Option("Không áp dụng", "")
    );

    rateTypeSelect.disabled = true;
}

function updateForm() {
    updateCurrencyOptions();
    updateRateType();
}


// ==========================================
// GHI NHỚ LỰA CHỌN MUA CỦA NGƯỜI DÙNG
// ==========================================

rateTypeSelect.addEventListener("change", function () {
    if (
        rateTypeSelect.value === "transfer" ||
        rateTypeSelect.value === "cash"
    ) {
        selectedBuyType = rateTypeSelect.value;
    }
});


// ==========================================
// NÚT ĐỔI CHIỀU TIỀN TỆ
// ==========================================

swapButton.addEventListener("click", function () {
    const oldFrom = fromCurrency.value;
    const oldTo = toCurrency.value;

    // Mở lại các option trước khi đổi chiều,
    // vì một số option đang bị lọc bởi Vietcombank.
    setCurrencyOptions(fromCurrency, () => true);
    setCurrencyOptions(toCurrency, () => true);

    fromCurrency.value = oldTo;
    toCurrency.value = oldFrom;

    updateForm();
});


// ==========================================
// CẬP NHẬT KHI ĐỔI NGUỒN HOẶC TIỀN TỆ
// ==========================================

sourceSelect.addEventListener("change", updateForm);
fromCurrency.addEventListener("change", updateForm);
toCurrency.addEventListener("change", updateForm);


// Khôi phục giao diện khi trang tải lần đầu
// hoặc tải lại sau khi bấm Chuyển đổi.
updateForm();