import { DeepPartial, EntityRepository, FindOptionsWhere, Repository } from 'typeorm';
import { Data } from './data.entity';

@EntityRepository(Data)
export class DataRepository extends Repository<Data> {
	async findAll(): Promise<Data[]> {
		return await this.find();
	}

	async findOneBy(args: FindOptionsWhere<Data>): Promise<Data> {
		return await this.findOneBy(args);
	}

	async createData(createDataInput: DeepPartial<Data>): Promise<Data> {
		const data = this.create(createDataInput);
		return await this.save(data);
	}

	async removeData(arg: FindOptionsWhere<Data>): Promise<Data> {
		const data = await this.findOneBy(arg);
		await this.remove(data);
		return new Data('', '', '', false);
	}
}
