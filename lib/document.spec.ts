import { unlinkSync } from 'fs'
import { join } from 'path'
import * as test from 'tape'
import { Document } from './document'
import { EncryptInitOption, Encrypt } from './encrypt';
import { Obj } from './object';
import { Dictionary } from './dictionary';

const filePath = join(__dirname, '../test.pdf'),
    outFile = './test.out.pdf',
    uPwd = 'secret',
    pwdDoc = join(__dirname, '../pwd.pdf')

test('Can load a pdf', t => {
    let doc: Document
    try {
        doc = new Document(filePath)
    }
    catch (e) {
        t.fail()
    }
    t.end()
})

test('document requires password', t => {
    let doc: Document
    try {
        doc = new Document(pwdDoc)
    }
    catch (e) {
        t.ok(e instanceof Error, 'should throw an error')
        t.assert((e.message as string).startsWith("Password"), 'password required error')
        t.end()
    }
})

test('throws JS error on file not found', t => {
    let doc: Document
    try {
        doc = new Document('/bad/path')
    } catch (e) {
        t.ok(e instanceof Error, 'should throw error')
        t.end();
    }
})

test('encryption: user password', t => {
    const doc = new Document(filePath),
        encryptionOption: EncryptInitOption = {
            ownerPassword: 'secret',
            keyLength: 40,
            protection: ['Edit', 'FillAndSign'],
            algorithm: 'aesv3'
        },
        secureDoc = join(__dirname, '../secure.pdf'),
        enc = new Encrypt(null, encryptionOption)

    doc.encrypt = enc
    doc.write(secureDoc)

    let sDoc: Document = new Document(secureDoc),
        trailer: Obj = sDoc.getTrailer()
    let trailerDict = new Dictionary(trailer)
    if (!doc.encrypt) {
        t.fail()
    }
    const fillAndSign = doc.encrypt.isAllowed('FillAndSign'),
        edit = doc.encrypt.isAllowed('Edit')

    t.assert(trailerDict.hasKey("Encrypt") === true, 'trailer has an encryption object')
    t.end()
})

test('document get page count', t => {
    const doc = new Document(filePath)
    const pc = doc.getPageCount()
    t.ok(pc)
    t.assert(pc > 0)
    t.end()
})
test('document delete page', t => {
    const doc = new Document(filePath),
        pc = doc.getPageCount()

    doc.deletePage(pc - 1)
    doc.write(outFile)

    const docLessOne = new Document(outFile),
        docLessOnePageCount = docLessOne.getPageCount()
    t.assert(pc === docLessOnePageCount + 1)
    unlinkSync(outFile)
    t.end()
})
test('document merger', t => {
    const doc = new Document(filePath),
        originalPC = doc.getPageCount()

    doc.mergeDocument(filePath)
    doc.write(outFile)

    const doc2 = new Document(outFile),
        doc2PC = doc2.getPageCount()

    t.assert(originalPC * 2 === doc2PC, "merged document")
    unlinkSync(outFile)
    t.end()
})
test('get page', t => {
    const doc = new Document(filePath),
        page = doc.getPage(0) // pages are zero indexed
    t.ok(page)
    t.end()
})

test('Document set encrypt', t => {
    t.end()
})
