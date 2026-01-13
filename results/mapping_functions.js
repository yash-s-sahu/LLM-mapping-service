function log(message) {
  const prefix = 'GraalVM:MessageJS:ProcessPurchaseOrder-Inbound:';
  console.log(prefix + message);
}

/**
 * Concatenates SourceTransactionId string as per XSL: '01-' + partnerKey1 + '-' + poNumber.
 * @param {string} partnerKey1 - First partner key.
 * @param {string} poNumber - Purchase Order Number.
 * @returns {string} - SourceTransactionId.
 */
function concatSourceTransactionId(partnerKey1, poNumber) {
  log('concatSourceTransactionId:partnerKey1: ' + partnerKey1 + ', poNumber: ' + poNumber);
  const result = '01-' + partnerKey1 + '-' + poNumber;
  log('concatSourceTransactionId:result: ' + result);
  return result;
}

/**
 * Concatenates subline SourceTransactionId as per XSL: '01-' + partnerKey1 + '-' + poNumber.
 * Subline IDs match line unless additional structure, but for unique lines, add -subLine for clarity.
 * @param {string} partnerKey1
 * @param {string} poNumber
 * @param {string} parentLineNumber
 * @param {string} subLineNumber
 * @returns {string} - SourceTransactionId for subline as '01-partnerKey1-poNumber' (same as line).
 */
function concatSubLineSourceTransactionId(partnerKey1, poNumber, parentLineNumber, subLineNumber) {
  log('concatSubLineSourceTransactionId:partnerKey1: ' + partnerKey1 + ', poNumber: ' + poNumber + ', parentLineNumber: ' + parentLineNumber + ', subLineNumber: ' + subLineNumber);
  // Matches regular SourceTransactionId, no unique subline value by XSL.
  const result = '01-' + partnerKey1 + '-' + poNumber;
  log('concatSubLineSourceTransactionId:result: ' + result);
  return result;
}

/**
 * Concatenates a main line and subline number into the expected sourceTransactionLineId and scheduleId, e.g., '101-102'.
 * @param {string} parentLineNumber
 * @param {string} subLineNumber
 * @returns {string} - Format 'parentLineNumber-subLineNumber'
 */
function concatLineAndSubLine(parentLineNumber, subLineNumber) {
  log('concatLineAndSubLine:parentLineNumber: ' + parentLineNumber + ', subLineNumber: ' + subLineNumber);
  const result = parentLineNumber + '-' + subLineNumber;
  log('concatLineAndSubLine:result: ' + result);
  return result;
}