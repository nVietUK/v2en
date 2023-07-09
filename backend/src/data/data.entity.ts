import { Field, InputType, ObjectType } from '@nestjs/graphql';
import { Md5 } from 'ts-md5';
import { Column, Entity, PrimaryColumn, PrimaryGeneratedColumn } from 'typeorm';
import { IsDataExistedByHashValue } from './data.validator';

@Entity()
@ObjectType('DataObject')
@InputType('DataInput')
export class Data {
	constructor(origin = '', translated = '', translator = '', verified = false) {
		this.origin = origin;
		this.translated = translated;
		this.translator = translator;
		this.verified = verified;
	}

	@PrimaryGeneratedColumn()
	@PrimaryColumn('int')
	id?: number;

	@Field(() => String, { description: 'the origin of sentence' })
	@Column('longtext')
	origin: string;

	@Column('longtext')
	@Field(() => String, { description: 'the translated of sentence' })
	translated: string;

	@Field(() => String)
	get object() {
		return `origin: ${this.origin};  translated: ${this.translated}`;
	}

	@Column('longtext')
	@Field(() => String, { description: "the sentence's translator" })
	translator: string;

	@Column('longtext', { nullable: false })
	@IsDataExistedByHashValue({ message: 'hashValue is exited' })
	get hashValue(): string {
		return Md5.hashStr(
			`${this.origin} ${this.translated} ${this.translator}`,
		).toString();
	}
	set hashValue(value: string) {
		value;
	}

	@Column({ default: false })
	@Field(() => Boolean, { description: 'confirm that data is verified by authorizer' })
	verified: boolean;
}
