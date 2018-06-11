# -*- coding: UTF-8 -*-

import xml.dom.minidom

class itemtype:
    type_int32 = 0
    type_uint32 = 1
    type_int64 = 2
    type_uint64 = 3
    type_acsii = 4
    type_decimal = 5
    type_byteVector = 6
    type_sequence = 7
    type_length = 8
    type_typeRef = 9
    type_else = 100

def toitemtype(strtype):
    if strtype == 'string':
        return itemtype.type_acsii
    elif strtype == 'int32':
        return itemtype.type_int32
    elif strtype == 'int64':
        return itemtype.type_int64
    elif strtype == 'uint32':
        return itemtype.type_uint32
    elif strtype == 'length':
        return itemtype.type_length
    elif strtype == 'uint64':
        return itemtype.type_uint64
    elif strtype == 'decimal':
        return itemtype.type_decimal
    elif strtype == 'bytevector':
        return itemtype.type_byteVector
    elif strtype == 'sequence':
        return itemtype.type_sequence
    elif strtype == 'typeRef':
        return itemtype.type_typeRef
    else:
        return itemtype.type_else


class optype:
    op_no = 0  #   不占位  可选的用可空的表示方法进行编码，用NULL表示不存在
    op_copy = 1
    op_default = 2
    op_increment = 3  # op_increment op_copy   op_default   都占1位  可选的可以为空 NULl表示值不存在，此时除了default,前值状态也将设置为空
    #如果值在流中存在， 则成为新的前值  当值在流中不存在， 则根据前值的状态分为以下三种情况处理
    op_constant = 4  # 必要的  不占位   可选 占一位  如果该位被设置， 则值为指令上下文的初值
    op_delta = 5    #不占位，可选的可空，前值不被设为空， 而是保持不变
    op_tail = 6     #占位 可选的可空， 且前值被设置为空。

def tooptype(strtype):
    if strtype == 'copy':
        return optype.op_copy
    elif strtype == 'default':
        return optype.op_default
    elif strtype == 'constant':
        return optype.op_constant
    elif strtype == 'increment':
        return optype.op_increment
    elif strtype == 'delta':
        return optype.op_delta
    elif strtype == 'tail':
        return optype.op_tail
    else:
        return optype.op_no

#字段
class Field:
    def __init__(self):
        self.option = False #
        self.op = optype.op_no
        self.type = itemtype.type_int32 #
        self.prevalue = 0 #初值
        self.prevalueexist = False
        self.id = 0
        self.seq = 0
        self.items = []

    def additem(self,item):
        item.seq = len(self.items)
        self.items.append(item)

    def parsesequence(self,it):
        self.name = it.getAttribute('name')
        if it.hasAttribute('presence'):
            presence = it.getAttribute('presence')
            if presence == "optional":
                self.option = True
        for child in it.childNodes:
            if child.nodeType == xml.dom.minidom.Node.ELEMENT_NODE:
                item = Field()
                if item.parse_element(child):
                    if len (self.items) == 0:
                        if( item.type == itemtype.type_length ):
                            self.seqlen_item = item #序列长度item
                            continue
                    self.additem(item)
        return True

    def parse_element(self,it):
        self.type = toitemtype(it.nodeName.lower())
        self.name = it.getAttribute('name')
        if self.type == itemtype.type_else:
            return False
        if self.type == itemtype.type_typeRef:
            return False
        if self.type == itemtype.type_sequence:
            return self.parsesequence(it)
            pass
        self.id = it.getAttribute('id')
        # print self.id,self.type
        # print self.id,len(it.childNodes)
        if it.hasAttribute('presence'):
            presence = it.getAttribute('presence')
            if presence == "optional":
                self.option = True
        for child in it.childNodes:
            if child.nodeType == xml.dom.minidom.Node.ELEMENT_NODE:
                optype = child.nodeName
                # print it.childNodes[0].toxml(),len(it.childNodes)
                # print child.nodeName
                self.op = tooptype(optype)
                if child.hasAttribute('value'):
                    self.prevalue = child.getAttribute('value')
                    self.prevalueexist = True
                break
        return True
        pass

    #是否需要占位
    def needplace(self):
        if self.op in (optype.op_no,optype.op_delta):
            return False
        elif self.op in (optype.op_copy,optype.op_default,optype.op_increment,optype.op_tail):
            return True
        elif self.op == optype.op_constant:
            if self.option:
                return True
            else:
                return False

class message:
    def __init__(self):
        self.Fields = []
    def additem(self,item):
        item.seq = len(self.Fields)
        self.Fields.append(item)

    def parse_element(self,templat):
        self.messageid = int(templat.getAttribute('id'))
        self.msgname = templat.getAttribute('name')
        # print self.messageid
        item = Field()
        item.id = self.messageid
        self.additem(item)
        for it in templat.childNodes:
            if it.nodeType == xml.dom.minidom.Node.ELEMENT_NODE:
                item = Field()
                if item.parse_element(it):
                    self.additem(item)
                # print it,it.nodeName,it.nodeType
                # break
        return True

class template:
    def __init__(self):
        self.messageitems = {}

    def load(self,filename):
        domt = xml.dom.minidom.parse(filename)
        rootnode = domt.documentElement
        templates = rootnode.getElementsByTagName('template')
        for templat in templates:
            nmesage = message()
            if nmesage.parse_element(templat):
                self.additem(nmesage)
        print filename,rootnode,domt

    def additem(self,item):
        print "message", item.messageid
        self.messageitems[item.messageid] = item

    def getmessage(self,msgid):
        if self.messageitems.has_key(msgid):
            return True,self.messageitems[msgid]
        else:
            return False,1

if __name__ == '__main__':
    print 'template test'
    tem = template()
    tem.load('C:\Users\gao\PycharmProjects/test\shstep/template.xml')
